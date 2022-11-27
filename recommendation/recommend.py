import joblib
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# import User_Recommend packages
import pandas as pd
import psycopg2

# neo4j 드라이버 import 및 함수 정의
from neo4j import GraphDatabase

## Content_Recommend packages
# import packages
import numpy as np

grade_df = pd.read_excel('2020_27890_grade_df.xlsx')

course_key = pd.read_excel('key.xlsx', header=None)

class Neo4jConnection:
    
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
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
            session = self.__driver.session(database=db) if db is not None else self.__driver.session() 
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
      self.connection_info = "host=147.47.200.145 dbname=teamdb5 user=team5 password=snugraduate port=34543" # PostgreSQL 연결 주소


  def connect_SQL(self): # DB에서 데이터를 불러옴
    # PostgreSQL 연결
    conn = psycopg2.connect(self.connection_info)

    try:
        # 테이블을 Pandas.Dataframe으로 추출 (user table, course table, enrollment table)
        self.user = pd.read_sql('SELECT id, username FROM auth_user ',conn)   # user table
        self.course = pd.read_sql('SELECT cid_int, cid, cname FROM check_course',conn)  # check_course table
        self.enroll = pd.read_sql('SELECT cid_int, user_id, cid from exp_enrollment',conn)  # enroll table  # exp -> rec # 최신데이터만 가져오는 부분이 있어야 할듯 (user_id별로 가장 큰 up_id만 가져온다거나)
        
    except psycopg2.Error as e:
        # 데이터베이스 에러 처리
        print("DB error: ", e)
        
    finally:
        # 데이터베이스 연결 해제 필수!! 
        conn.close()

    self.enroll_idx = self.enroll.set_index('user_id')

  def connect_Neo4j(self, id, cnt): # 조건 쿼리, input : id - User ID / cnt : 몇명을 리턴할것인가? (default = 3)
    # DB Connection Information
    dbname = "teamdb5"
    uri_param = "bolt://147.47.200.145:37687"
    user_param = "team5"
    pwd_param = "snugraduate"
    apoc_string = 'CALL apoc.load.jdbc("jdbc:postgresql://localhost:34543/teamdb5?user=team5&password=snugraduate",'

    # Neo4j 연결
    conn = Neo4jConnection(uri=uri_param, user=user_param, pwd=pwd_param)
    # Cypher 쿼리 입력
    cypher = (apoc_string + '"exp_enrollment") YIELD row '              # exp -> rec # 여기도 최신데이터만 가져오도록 고쳐야 할듯
              'MERGE (sd:Student {id: row.user_id}) '                     # User Node 형성
              'MERGE (c:Course {cid_int: toInteger(row.cid_int)}) '  # 과목 Node 형성
              'MERGE (sd)-[e:Enrollment {gpa : row.gpa}]->(c) '  # 수강 Flow 형성
              'with sd,c '                                         
              'Match (sd{id:'+ str(id) + '})-->(c)<--(sd2) '         # User과 들은 과목을 들은 sd2를 찾아라
              'return distinct sd2.id, count(*) as cnt '              # sd2의 user id 반환
              'order by cnt desc '                                   # 겹치는 과목의 순서가 많은 사람부터
              'Limit '+ str(cnt)                                     # cnt명 반환
              )

    # Cypher 쿼리 실행 후 결과를 print
    response = conn.query(cypher, db=dbname)

    #모든 노드 삭제 - 초기화 필수!!
    conn.query('MATCH (n) DETACH DELETE n', db=dbname)    

    # 연결 종료 필수!
    conn.close()

    if response == None:      # 예외 처리 : 유사한 사용자가 없으면 전체 과목 리턴
      return list(self.course['cid']) # 전체 과목 id list
      
    person = pd.DataFrame([dict(record) for record in response])
    # # print(person) # sd id 확인용
    if person.shape[0] < cnt :  # 예외 처리 : 특정 인원수가 안되면 그냥 전체 과목을 리턴
      return list(self.course['cid'])  # 전체 과목 id list

    # dictionray - 유저 확인용
    # cid_list = {}
    # for idx,i in person['sd2.id'].iteritems():
    #   cid_list[i] = list(self.enroll_idx['cid_int'].loc[i])
    # return cid_list

    cid_list = []
    for idx,i in person['sd2.id'].iteritems():
      cid_list+=list(self.enroll_idx['cid'].loc[i]) # 비슷한 과목을 들은 유저들의 과목을 리스트화
    cid_set = set(cid_list) # 중복 제거
    cid_list = list(cid_set) # 중복 제거

    for value in list(self.enroll_idx['cid'].loc[id]): # list에서 user가 들은 과목 제거
      if value in cid_list: # 조건추가 (혜령): user가 들은 과목중에 cid_list에 없는 과목이 있을 수도 있으므로 체크 필요
        cid_list.remove(value)

    # cid_list=[]
    # for i in cid_int_list:
    #   cid_list.append(self.course.set_index('cid_int')['cid'].loc[i])
    # cid_list

    cid_list.sort() # 오름차순 정렬

    return cid_list

  def get_person(self, id, cnt=3):  # 3명의 비슷한 유저를 찾아라
    self.connect_SQL()  # DB에서 데이터 로드
    return self.connect_Neo4j(id, cnt) # Candidate cnt명을 찾고 그들의 과목 cid_int 반환

import psycopg2
import psycopg2.extras as extras

# 연결정보 입력
connection_info = "host=147.47.200.145 dbname=teamdb5 user=team5 password=snugraduate port=34543"

# PostgreSQL 연결
# conn = psycopg2.connect(connection_info)

def select_from(conn, query):

  try:
      df = pd.read_sql(query,conn)

  except Exception as e:
      df = pd.DataFrame()
      print("Error: ", e)
      
  finally:
      conn.close()
      return df

class Recommender():
  def __init__(self, 
               file_dir = './', 
               tfidf_fname = 'tfidf_tdm.pkl', 
               cid_fname = 'cid_list.pkl'):
    self.tfidf = joblib.load(os.path.join(file_dir, tfidf_fname))
    self.cid_list = joblib.load(os.path.join(file_dir, cid_fname))

  def get_content_based_candidates(self, 
                                   grade_df,
                                   corpus = None,
                                   k = 10):
      
      # generate user representations
      tfidf_list = []
      indices = []
      for cid in grade_df['cid']:
        if cid == 'M3239.002000':  # 데이터사이언스 대학원논문연구
          continue
        idx = np.where(self.cid_list==cid)[0]
        if len(idx) == 0:
          print(f"{cid} not in list")
          continue 
        else: 
          indices.append(idx)
        tfidf_list.append(self.tfidf[idx,:].toarray())
      user_embed = np.mean(np.stack(tfidf_list), axis=0)
        
      # calculate cosine similarity
      item_embed = self.tfidf
      cosine_sim = cosine_similarity(user_embed, item_embed)

      sim_scores = list(enumerate(cosine_sim[0]))
      sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
      sim_scores = [x for x in sim_scores if x[0] not in indices] # drop indices of already taken courses
      if corpus is not None:
        corpus_intersect = set(self.cid_list).intersection(set(corpus))
        if len(corpus_intersect) > 0:
          corpus_indices = [np.where(self.cid_list==x)[0][0] for x in corpus_intersect]
          sim_scores = [x for x in sim_scores if x[0] in corpus_indices]
      sim_scores = sim_scores[1:k+1]
      rec_indices = [i[0] for i in sim_scores]

      return self.cid_list[np.array(rec_indices)]

  def get_user_based_candidates(self,
                                user_id,
                                grade_df,
                                k=10,
                                cnt=3):
    generator=Candidate_user_generate() # Class Instance 선언
    # cid_list 생성
    try:
      generated_list=generator.get_person(user_id, cnt=cnt) # input = user id , output = cid_int list
    except psycopg2.Error as e:
      try:
        generated_list=generator.get_person(user_id, cnt=cnt) # input = user id  # 커넥팅 에러 방지차원으로 한번 더 실행
      except psycopg2.Error as e:
        try:
          generated_list=generator.get_person(user_id, cnt=cnt) # input = user id  # 커넥팅 에러 방지차원으로 한번 더 실행
        except psycopg2.Error as e:
          # 데이터베이스 에러 처리
          print("DB error: ", e)
    return self.get_content_based_candidates(grade_df, generated_list, k=k)

  def get_recommendation(self, user_id, grade_df, k=10, similar_user_cnt=3):
    candidates_content = rec.get_content_based_candidates(grade_df, k=k)
    candidates_user = rec.get_user_based_candidates(user_id, grade_df, k=k, cnt=similar_user_cnt)
    rec_list = list(set(candidates_content) | set(candidates_user))

    connection_info = "host=147.47.200.145 dbname=teamdb5 user=team5 password=snugraduate port=34543"
    conn = psycopg2.connect(connection_info)
    query2 = "SELECT a.cid, a.cname, a.program, a.classification, b.crd, a.dept, a.lang, a.yr_sem, a.last_yr_sem FROM (SELECT * FROM rec_courses WHERE cid IN (%s)) a LEFT JOIN check_course b ON a.cid=b.cid;" % str(rec_list)[1:-1]
    return select_from(conn, query2)

query2 = "SELECT * FROM rec_courses WHERE cid IN (%s);" % str(list(set1|set2))[1:-1]
print(query2)

uid3_grade_df = pd.DataFrame({'cid': ['106.746',
'107.247',
'M3239.003000',]})

## to-do -> sort the list by similarity score # show avg_quota?

# %%timeit
rec = Recommender()
# candidates_content = rec.get_content_based_candidates(grade_df)
rec.get_recommendation(3, uid3_grade_df)