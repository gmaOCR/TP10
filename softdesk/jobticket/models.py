from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models


class Project(models.Model):
    CHOICES = (
        ('W', 'Web'),
        ('IOS', 'iOS'),
        ('A', 'Android'),
    )
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, validators=[MinLengthValidator(20)])
    type = models.CharField(
        max_length=10, choices=CHOICES, verbose_name='type'
    )
    author_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )


class Contributors(models.Model):
    CHOICES_PERM = (
        ('C', 'Create'),
        ('R', 'Read'),
        ('U', 'Update'),
        ('D', 'Delete')
    )

    CHOICE_ROLE = (
        ('Resp', 'Responsable'),
        ('Auteur', 'Auteur'),
        ('Contrib', 'Contributeur')
    )

    role = models.CharField(max_length=15, choices=CHOICE_ROLE)
    permission = models.CharField(max_length=15, choices=CHOICES_PERM)


class Issues(models.Model):
    title = models.CharField(max_length=200)
    desc = models.CharField(max_length=2000, validators=[MinLengthValidator(20)])
    tag = models.CharField(max_length=200)
    status
    author_user
    assigned_to
    created_time
