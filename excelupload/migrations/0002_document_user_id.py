# Generated by Django 4.1.3 on 2022-11-26 23:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('excelupload', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name = 'document',
            name = 'user_id',
            field = models.ForeignKey(default = 1, on_delete = django.db.models.deletion.CASCADE, to = settings.AUTH_USER_MODEL, verbose_name = 'user'),
            preserve_default = False,
        ),
    ]