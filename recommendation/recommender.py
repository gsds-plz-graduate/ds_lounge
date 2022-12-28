# -*- coding: utf-8 -*-
import os
import warnings

import joblib
import numpy as np
import pandas as pd
import psycopg2
from django.conf import settings
from django.db.models import Max
from neo4j import GraphDatabase
from sklearn.metrics.pairwise import cosine_similarity

from check.models import CheckCourse, Enrollment
from group_project.settings import env

warnings.filterwarnings(action = 'ignore')


## 다음 에러 때문에 filterwarnings 추가
## UserWarning: pandas only support SQLAlchemy connectable(engine/connection) ordatabase string URI or sqlite3 DBAPI2 connectionother DBAPI2 objects are not tested, please consider using SQLAlchemy

class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(
                self.__uri, auth=(self.__user, self.__pwd)
            )
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = (
                self.__driver.session(database=db)
                if db is not None
                else self.__driver.session()
            )
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response


class Candidate_user_generate:
    def __init__(self):
        # DB Connection Information
        self.connection_info = env("POSTGRESQL_INFO")  # PostgreSQL 연결 주소

    def connect_SQL(self):  # DB에서 데이터를 불러옴
        # PostgreSQL 연결
        conn = psycopg2.connect(self.connection_info)

        try:
            # 테이블을 Pandas.Dataframe으로 추출 (user table, course table, enrollment table)
            self.user = pd.read_sql(
                "SELECT id, username FROM auth_user ", conn
            )

            # user table
            # self.course = pd.read_sql(
            #     "SELECT cid_int, cid, cname FROM check_course", conn
            # )  # check_course table

            course = CheckCourse.objects.all().values('cid_int', 'cid', 'cname')
            self.course = pd.DataFrame(list(course))

            # ################################################################################################ 12.02 max_up id 쿼리 수정
            # self.enroll = pd.read_sql(
            #     "SELECT cid_int, user_id, cid from rec_enrollment where up_id in (select max(re.up_id) from rec_enrollment re group by re.user_id)",
            #     conn,
            # )  # enroll table  # exp -> rec # 최신데이터만 가져오는 부분이 있어야 할듯 (user_id별로 가장 큰 up_id만 가져온다거나)
            # ################################################################################################
            # self.enroll_idx = self.enroll.set_index("user_id")

            rec_up_ids = list(Enrollment.objects.values('user_id').annotate(rec_up_id = Max('up_id')).values_list('rec_up_id', flat = True))
            rec_enrollment = Enrollment.objects.filter(up_id__in = rec_up_ids).values('cid_int', 'user_id', 'cid')
            self.enroll = pd.DataFrame(list(rec_enrollment))
            self.enroll_idx = self.enroll.set_index("user_id")

        except psycopg2.Error as e:
            # 데이터베이스 에러 처리
            print("DB error: ", e)

        finally:
            # 데이터베이스 연결 해제 필수!!
            conn.close()

    def connect_Neo4j(
        self, id, cnt
    ):  # 조건 쿼리, input : id - User ID / cnt : 몇명을 리턴할것인가? (default = 3)
        # DB Connection Information
        dbname = env("NAME")
        uri_param = env("NEO4J_URI")
        user_param = env("USER")
        pwd_param = env("PASSWORD")
        apoc_string = env("APOC_STRING")

        # Neo4j 연결
        conn = Neo4jConnection(uri=uri_param, user=user_param, pwd=pwd_param)
        # Cypher 쿼리 입력
        ################################################################################################     12.02 up_id 쿼리문 변경
        cypher = (
            apoc_string
            + '"SELECT cid_int, user_id, cid, up_id, gpa from rec_enrollment where up_id IN (select max(re.up_id) from rec_enrollment re group by re.user_id)") YIELD row '  # exp -> rec # 여기도 최신데이터만 가져오도록 고쳐야 할듯
            "MERGE (sd:Student {id: row.user_id, up_id: row.up_id}) "  # User Node 형성
            "MERGE (c:Course {cid: row.cid}) "  # 과목 Node 형성
            "MERGE (sd)-[e:Enrollment {gpa : row.gpa}]->(c) "  # 수강 Flow 형성
            "with sd,c "
            "Match (sd{id:" + str(id) + "})-->(c)<--(sd2) "  # User과 들은 과목을 들은 sd2를 찾아라
            "return distinct sd2.id, count(*) as cnt "  # sd2의 user id 반환
            "order by cnt desc "  # 겹치는 과목의 순서가 많은 사람부터
            "Limit " + str(cnt)  # cnt명 반환
        )
        ################################################################################################
        # Cypher 쿼리 실행 후 결과를 print
        response = conn.query(cypher, db=dbname)

        # 모든 노드 삭제 - 초기화 필수!!
        conn.query("MATCH (n) DETACH DELETE n", db=dbname)

        # 연결 종료 필수!
        conn.close()

        # user_list = list(self.enroll_idx['cid'].loc[id]) # User가 들은 과목

        # 예외 처리 : 유사한 사용자가 없으면 전체 과목 리턴
        if response is None:
            ################################################################################################
            result_list = list(self.course["cid"])  # 전체 과목 id list
            for value in list(self.enroll_idx["cid"].loc[id]):  # User가 들은 과목 제외
                if (
                        value in result_list
                ):  # 조건추가 (혜령): user가 들은 과목중에 cid_list에 없는 과목이 있을 수도 있으므로 체크 필요
                    result_list.remove(value)
            return result_list
        ################################################################################################

        person = pd.DataFrame([dict(record) for record in response])
        # # print(person) # sd id 확인용
        ############################################################################################### 12.02 모집 인원수가 적어 해당 조건 삭제
        # # 예외 처리 : 특정 인원수가 안되면 그냥 전체 과목을 리턴
        # if person.shape[0] < cnt :
        # ################################################################################################
        #   result_list = list(self.course['cid']) # 전체 과목 id list
        #   for value in list(self.enroll_idx['cid'].loc[id]): # # 조건추가 (영훈) : DS 필수과목 제외
        #     if value in result_list: # 조건추가 (혜령): user가 들은 과목중에 cid_list에 없는 과목이 있을 수도 있으므로 체크 필요
        #       result_list.remove(value)
        #   return result_list
        # ################################################################################################
        ###############################################################################################

        # dictionray - 유저 확인용
        # cid_list = {}
        # for idx,i in person['sd2.id'].iteritems():
        #   cid_list[i] = list(self.enroll_idx['cid_int'].loc[i])
        # return cid_list

        cid_list = []
        for idx, i in person["sd2.id"].iteritems():
            cid_list += list(self.enroll_idx["cid"].loc[i])  # 비슷한 과목을 들은 유저들의 과목을 리스트화
        cid_set = set(cid_list)  # 중복 제거
        cid_list = list(cid_set)  # 중복 제거

        for value in list(self.enroll_idx["cid"].loc[id]):  # list에서 user가 들은 과목 제거
            if (
                value in cid_list
            ):  # 조건추가 (혜령): user가 들은 과목중에 cid_list에 없는 과목이 있을 수도 있으므로 체크 필요
                cid_list.remove(value)

        # for value in check_list: # # 조건추가 (영훈) : DS 필수과목 제외
        #   if value in cid_list: # 조건추가 (혜령): user가 들은 과목중에 cid_list에 없는 과목이 있을 수도 있으므로 체크 필요
        #     cid_list.remove(value)

        # cid_list=[]
        # for i in cid_int_list:
        #   cid_list.append(self.course.set_index('cid_int')['cid'].loc[i])
        # cid_list

        # cid_list.sort() # 오름차순 정렬

        return cid_list

    def get_person(self, id, cnt=3):  # 3명의 비슷한 유저를 찾아라
        self.connect_SQL()  # DB에서 데이터 로드
        return self.connect_Neo4j(id, cnt)  # Candidate cnt명을 찾고 그들의 과목 cid_int 반환


class Recommender:
    def __init__(
        self, file_dir="./", tfidf_fname="tfidf_tdm.pkl", cid_fname="cid_list.pkl"
    ):
        self.tfidf = joblib.load(os.path.join(settings.BASE_DIR, file_dir, tfidf_fname))
        self.cid_list = joblib.load(os.path.join(file_dir, cid_fname))
        ################################################################################################
        self.basecourse_list = [  # DS 필수과목 리스트
            "M3239.000100",
            "M3239.000200",
            "M3239.000300",
            "M3239.003800",
            "M3239.005000",
            "M3239.005100",
            "M3239.005300",
            "M3239.005400",
            "M3239.005500",
            "M3239.005700",
            "M3239.006700",
            "M3239.002800",
            "M3239.003000",
            "M3239.000400",
            "M3239.000500",
            "M3239.000900",
            "M3239.005800",
            "M3239.003300",
            "M3239.002000",
            "M3239.005600",
            "M3239.005800",
        ]
        ################################################################################################

    def get_content_based_candidates(self, grade_df, corpus=None, k=10):

        # generate user representations
        tfidf_list = []
        for cid in grade_df["cid"]:
            idx = np.where(self.cid_list == cid)[0]
            if len(idx) == 0:  # 'M3239.002000' 데이터사이언스 대학원논문연구 를 포함해 cid_list에 없는 과목 존재
                # print(f"{cid} not in list")
                continue
            tfidf_list.append(self.tfidf[idx, :].toarray())
        user_embed = np.mean(np.stack(tfidf_list), axis=0)

        # calculate cosine similarity
        item_embed = self.tfidf
        cosine_sim = cosine_similarity(user_embed, item_embed)[0]

        # filter cid_list based on similarity, corpus, and whether already taken
        sim_scores = list(zip(self.cid_list, cosine_sim))
        ################################################################################################
        sim_scores = [
            x
            for x in sim_scores
            if (x[0] not in grade_df["cid"].tolist())
            and (x[1] > 0)
            and (x[0] not in self.basecourse_list)
        ]  # drop indices of already taken courses # drop courses with 0 similarity
        ################################################################################################
        if corpus is not None:
            corpus_intersect = set(self.cid_list).intersection(set(corpus))
            if len(corpus_intersect) > 0:
                sim_scores = [x for x in sim_scores if x[0] in corpus_intersect]

        # return top k
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[:k]
        return sim_scores

    def get_user_based_candidates(self, user_id, grade_df, k=10, cnt=3):
        generator = Candidate_user_generate()  # Class Instance 선언
        # cid_list 생성
        try:
            generated_list = generator.get_person(
                user_id, cnt=cnt
            )  # input = user id , output = cid_int list
        except psycopg2.Error as e:
            try:
                generated_list = generator.get_person(
                    user_id, cnt=cnt
                )  # input = user id  # 커넥팅 에러 방지차원으로 한번 더 실행
            except psycopg2.Error as e:
                try:
                    generated_list = generator.get_person(
                        user_id, cnt=cnt
                    )  # input = user id  # 커넥팅 에러 방지차원으로 한번 더 실행
                except psycopg2.Error as e:
                    # 데이터베이스 에러 처리
                    print("DB error: ", e)
        return self.get_content_based_candidates(grade_df, generated_list, k=k)

    def get_recommendation(
            self, user_id, grade_df, include_undergrad = True, k = 10, similar_user_cnt = 3
    ):
        candidates_scores_content = self.get_content_based_candidates(grade_df, k = k)
        candidates_scores_user = self.get_user_based_candidates(
            user_id, grade_df, k = k, cnt = similar_user_cnt
        )

        rec_scores = set(candidates_scores_content + candidates_scores_user)
        rec_list = sorted(rec_scores, key = lambda x: x[1], reverse = True)
        rec_list = [x[0] for x in rec_list]

        connection_info = env("POSTGRESQL_INFO")
        conn = psycopg2.connect(connection_info)
        query = (
                "SELECT a.cid, a.cname, a.program, a.classification, b.crd, a.dept, a.lang, a.yr_sem, a.last_yr_sem FROM (SELECT * FROM rec_courses WHERE cid IN (%s)) a LEFT JOIN check_course b ON a.cid=b.cid;"
            % str(rec_list)[1:-1]
        )

        try:
            df = pd.read_sql(query, conn)
        except Exception as e:
            print("Error: ", e)
        finally:
            conn.close()
        df = df.set_index("cid").loc[rec_list].reset_index()
        if not include_undergrad:
            df = df.loc[df["program"] == "대학원"].reset_index(drop = True)
        return df

# rec = Recommender(file_dir="data")
#
# if __name__ == "__main__":
#
#     uid = 2
#     connection_info = (
#         env("POSTGRESQL_INFO")
#     )
#     conn = psycopg2.connect(connection_info)
#
#     query = (
#         "SELECT cid_int, user_id, cid from rec_enrollment where up_id = (select max(re.up_id) from rec_enrollment re where user_id = %s)"
#         % uid
#     )
#
#     try:
#         user_grade_df = pd.read_sql(query, conn)
#     except Exception as e:
#         print("Error: ", e)
#     finally:
#         conn.close()
#     rec = Recommender(file_dir="data")
#     print(rec.get_recommendation(uid, user_grade_df))
#     print(rec.get_recommendation(uid, user_grade_df, include_undergrad=False))
