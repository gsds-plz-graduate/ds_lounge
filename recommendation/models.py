# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from allauth import app_settings
from django.db import models

from check.models import CourseKey


class Courses(models.Model):

    # 혜령: models 에 대해 잘모르는데,
    # 다른 파일 참고해서 rec_courses 테이블에 대응하는 class 정의해봤음.
    # 필요 없으면 지워도 됨.
    # 마음대로 수정해도되!
    cid = models.OneToOneField(CourseKey, models.CASCADE, db_column = 'cid', primary_key = True)
    program = models.CharField(max_length = 5, blank = True, null = True)
    cname = models.CharField(max_length = 100, blank = True, null = True)
    avg_quota = models.FloatField(blank = True, null = True)
    classification = models.CharField(max_length = 5, blank = True, null = True)
    dept = models.CharField(max_length = 255, blank = True, null = True)
    lang = models.CharField(max_length = 50, blank = True, null = True)
    yr_sem = models.CharField(max_length = 255, blank = True, null = True)
    last_yr_sem = models.CharField(max_length = 10, blank = True, null = True)
    notes = models.TextField(blank = True, null = True)

    class Meta:
        managed = True
        db_table = 'rec_courses'


class RecommendedResult(models.Model):

    ### recommendation module 이 리턴하는 결과
    ### 마음대로 수정해도되!
    user = models.ForeignKey(
        to = app_settings.USER_MODEL, verbose_name = "user", on_delete = models.CASCADE
    )
    cid = models.ForeignKey(to = CourseKey, on_delete = models.CASCADE, db_column = "cid")
    cname = models.CharField(max_length = 255, blank = True, null = True)
    program = models.CharField(max_length = 5, blank = True, null = True)
    classification = models.CharField(max_length = 5, blank = True, null = True)
    crd = models.IntegerField(blank = True, null = True)
    dept = models.CharField(max_length = 255, blank = True, null = True)
    lang = models.CharField(max_length = 50, blank = True, null = True)
    yr_sem = models.CharField(max_length = 255, blank = True, null = True)
    last_yr_sem = models.CharField(max_length = 10, blank = True, null = True)

    class Meta:
        db_table = ""
        managed = False
