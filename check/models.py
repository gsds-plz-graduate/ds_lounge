# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


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
