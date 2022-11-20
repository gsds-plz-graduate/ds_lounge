from django.core.validators import FileExtensionValidator
from django.db import models


# Create your models here.
class Document(models.Model):
    description = models.CharField(max_length = 255, blank = True)
    document = models.FileField(upload_to = 'documents/', validators = [FileExtensionValidator(allowed_extensions = ['xlsx'])])
    uploaded_at = models.DateTimeField(auto_now_add = True)
