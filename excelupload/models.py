from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models


# Create your models here.
class Document(models.Model):
    student_number = models.CharField(max_length = 10, validators = [RegexValidator(regex = r'20\d{2}-\d{5}/', inverse_match = True)], default = "")
    document = models.FileField(upload_to = 'documents/', validators = [FileExtensionValidator(allowed_extensions = ['xlsx'])])
    uploaded_at = models.DateTimeField(auto_now_add = True)
    degree_choices = (('석사', 'Master'), ('박사', 'Combined'), ('통합', 'Ph.D'))
    degree = models.CharField(max_length = 10, choices = degree_choices, default = '석사')
    bootMath = models.BooleanField(default = False)
    bootCom = models.BooleanField(default = False)
    paperTest = models.BooleanField(default = False)
