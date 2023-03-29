# Generated by Django 4.1.7 on 2023-03-27 14:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobticket', '0007_alter_project_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.CharField(max_length=1000, validators=[django.core.validators.MinLengthValidator(10)]),
        ),
    ]
