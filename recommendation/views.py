# Create your views here.
import warnings

import pandas as pd
from django.db.models import Max
from django.shortcuts import render

from check.models import Enrollment
from .recommender import Recommender

warnings.filterwarnings(action = "ignore")


## 다음 에러 때문에 filterwarnings 추가
## UserWarning: pandas only support SQLAlchemy connectable(engine/connection) ordatabase string URI or sqlite3 DBAPI2 connectionother DBAPI2 objects are not tested, please consider using SQLAlchemy

def recommend(request):
    user_id = request.user.id
    recommended_courses = recommendation(uid = user_id)
    return render(request, 'recommendation/recommendation.html', {'result': recommended_courses})


def recommendation(uid, include_undergrad = True):

    # query = (
    #     "SELECT cid_int, user_id, cid from rec_enrollment where up_id = (select max(re.up_id) from rec_enrollment re where user_id = %s)"
    #     % uid
    # )

    recommend_courses = []
    try:
        user_up_id = Enrollment.objects.filter(user_id = uid).aggregate(Max('up_id'))['up_id__max']
        user_grade_model = Enrollment.objects.filter(up_id = user_up_id)
        user_grade_df = pd.DataFrame(list(user_grade_model.values('cid_int', 'user_id', 'cid')))
        rec = Recommender(file_dir = "recommendation/data")

        machine_learning_recommend_courses = rec.get_recommendation(
            uid, user_grade_df, include_undergrad
        )

        recommend_courses = [machine_learning_recommend_courses.to_json()]
    except Enrollment.DoesNotExist:
        recommend_courses = []

    return recommend_courses
