# Generated by Django 3.2.5 on 2023-03-26 10:19

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jobticket', '0002_auto_20230325_1929'),
    ]

    operations = [
        migrations.AddField(
            model_name='contributor',
            name='project',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='contributor_project', to='jobticket.project'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contributor',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='authentication.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='issue',
            name='project',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='issue_project', to='jobticket.project'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comment',
            name='author_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_author', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='comment',
            name='issue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_issue', to='jobticket.issue'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='title',
            field=models.CharField(max_length=200, validators=[django.core.validators.MinLengthValidator(5)]),
        ),
        migrations.AlterField(
            model_name='project',
            name='author_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_author', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.CharField(max_length=1000, validators=[django.core.validators.MinLengthValidator(10)]),
        ),
        migrations.AlterField(
            model_name='project',
            name='title',
            field=models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(5)]),
        ),
    ]
