# Generated by Django 4.1.3 on 2022-11-21 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name = 'CustomUser',
            fields = [
                ('id', models.BigAutoField(auto_created = True, primary_key = True, serialize = False, verbose_name = 'ID')),
                ('password', models.CharField(max_length = 128, verbose_name = 'password')),
                ('last_login', models.DateTimeField(blank = True, null = True, verbose_name = 'last login')),
            ],
            options = {
                'abstract': False,
            },
        ),
    ]
