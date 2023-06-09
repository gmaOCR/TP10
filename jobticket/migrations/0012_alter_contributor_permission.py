# Generated by Django 4.1.7 on 2023-03-29 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobticket', '0011_alter_contributor_permission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contributor',
            name='permission',
            field=models.CharField(choices=[('R', 'Read'), ('C', 'Create'), ('U', 'Update'), ('D', 'Delete')], default='Read', max_length=15, verbose_name='Permissions'),
        ),
    ]
