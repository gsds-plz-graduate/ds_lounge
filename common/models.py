# Create your models here.
from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE
    )

    student_number = models.CharField(max_length = 10, null = True)
    degree_choices = (('석사', 'Master'), ('박사', 'Combined'), ('통합', 'Ph.D'))
    degree = models.CharField(max_length = 10, choices = degree_choices, default = '석사')
    passed = models.JSONField(default = dict)
    uploaded_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = 'user_extended'
