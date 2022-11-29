# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from allauth import app_settings
from django.contrib.auth.middleware import get_user
from django.db import models

from excelupload.models import Document


class CheckCourse(models.Model):
    cid_int = models.IntegerField(primary_key = True)
    cid = models.CharField(max_length = 255)
    cname = models.CharField(max_length = 255, blank = True, null = True)
    crd = models.IntegerField(blank = True, null = True)
    yr_20 = models.CharField(max_length = 255, blank = True, null = True)
    yr_21 = models.CharField(max_length = 255, blank = True, null = True)
    yr_22 = models.CharField(max_length = 255, blank = True, null = True)

    class Meta:
        managed = False
        db_table = 'check_course'


class CourseKey(models.Model):
    cid_int = models.IntegerField()
    cid = models.CharField(primary_key = True, max_length = 255)

    class Meta:
        managed = False
        db_table = 'course_key'


class Enrollment(models.Model):
    year = models.IntegerField(blank = True, null = True)
    cid = models.CharField(max_length = 255)
    cid_int = models.ForeignKey(to = CheckCourse, on_delete = models.CASCADE, db_column = 'cid_int')
    cname = models.CharField(max_length = 255, blank = True, null = True)
    crd = models.IntegerField(blank = True, null = True)
    gpa = models.CharField(max_length = 50, blank = True, null = True)
    gbn = models.CharField(max_length = 50, blank = True, null = True)
    re = models.BooleanField(default = False)
    up = models.ForeignKey(to = Document, on_delete = models.CASCADE)
    user = models.ForeignKey(to = app_settings.USER_MODEL, verbose_name = "user", on_delete = models.CASCADE)

    class Meta:
        managed = True
        db_table = 'rec_enrollment'

    @classmethod
    def enrollment_from_df(cls, row, up_id, request):
        record = cls(
            year = int(row.year),
            cid = row.cid,
            cid_int = CheckCourse.objects.get(cid_int = row.cid_int),
            cname = row.cname,
            crd = int(row.crd),
            gpa = row.gpa,
            gbn = row.gbn,
            re = row.re == "Y",
            up = Document.objects.get(up_id = up_id),
            user = get_user(request)
        )
        return record
