# Create your views here.
from rest_framework.response import Response
from .recommender import rec
import pandas as pd

import warnings

warnings.filterwarnings(action="ignore")
## 다음 에러 때문에 filterwarnings 추가
## UserWarning: pandas only support SQLAlchemy connectable(engine/connection) ordatabase string URI or sqlite3 DBAPI2 connectionother DBAPI2 objects are not tested, please consider using SQLAlchemy


def recommendation(uid, include_undergrad=True):
    import psycopg2

    connection_info = (
        "host=147.47.200.145 dbname=teamdb5 user=team5 password=snugraduate port=34543"
    )
    conn = psycopg2.connect(connection_info)

    query = (
        "SELECT cid_int, user_id, cid from rec_enrollment where up_id = (select max(re.up_id) from rec_enrollment re where user_id = %s)"
        % uid
    )

    try:
        user_grade_df = pd.read_sql(query, conn)
    except Exception as e:
        print("Error: ", e)
    finally:
        conn.close()

    machine_learning_recommend_courses = rec.get_recommendation(
        uid, user_grade_df, include_undergrad
    )
    recommend_courses = [machine_learning_recommend_courses.to_json()]
    return Response(recommend_courses)
