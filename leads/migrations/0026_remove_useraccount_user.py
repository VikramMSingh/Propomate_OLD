# Generated by Django 3.1.6 on 2021-04-29 05:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0025_useraccount_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useraccount',
            name='user',
        ),
    ]
