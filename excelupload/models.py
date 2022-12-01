from allauth import app_settings
from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models


# Create your models here.
class Document(models.Model):
    up_id = models.AutoField(auto_created = True, primary_key = True, serialize = False)
    student_number = models.CharField(max_length = 10, validators = [RegexValidator(regex = r'20\d{2}-\d{5}/', inverse_match = True)], default = "")
    document = models.FileField(upload_to = 'documents/', validators = [FileExtensionValidator(allowed_extensions = ['xlsx'])])
    uploaded_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    degree_choices = (('석사', 'Master'), ('박사', 'Combined'), ('통합', 'Ph.D'))
    degree = models.CharField(max_length = 10, choices = degree_choices, default = '석사')
    boot_math = models.BooleanField(default = False)
    boot_com = models.BooleanField(default = False)
    paper_test = models.BooleanField(default = False)
    share_yn = models.BooleanField(default = False)
    user = models.ForeignKey(app_settings.USER_MODEL, verbose_name = ("user"), on_delete = models.CASCADE)
