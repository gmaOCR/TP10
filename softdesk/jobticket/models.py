from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models


class Project(models.Model):
    CHOICES = (
        ('W', 'Web'),
        ('IOS', 'iOS'),
        ('A', 'Android'),
    )
    title = models.CharField(max_length=100, validators=[MinLengthValidator(5)])
    description = models.CharField(max_length=1000, validators=[MinLengthValidator(10)])
    type = models.CharField(
        max_length=10, choices=CHOICES, verbose_name='type'
    )
    author_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_author'
    )


class Contributor(models.Model):
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


class Issue(models.Model):
    TAG_CHOICES = (
        ('Bug', 'Bug'),
        ('Improv.', 'Amélioration'),
        ('Task', 'Tâches')
    )

    PRIORITY_CHOICES = (
        ('Low', 'Faible'),
        ('Medium', 'Moyen'),
        ('High', 'Elevée')
    )

    STATUS_CHOICES = (
        ('To do', 'A faire'),
        ('In prog', 'En cours'),
        ('Done', 'Terminé')
    )

    title = models.CharField(max_length=200, validators=[MinLengthValidator(5)])
    desc = models.CharField(max_length=2000, validators=[MinLengthValidator(20)])
    tag = models.CharField(max_length=20, choices=TAG_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    author_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='issue_author'
    )
    assigned_to = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='issue_assigned'
    )
    created_time = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    desc = models.CharField(max_length=2000, validators=[MinLengthValidator(5)])
    author_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comment_author'
    )
    issue = models.ForeignKey(
        to=Issue, on_delete=models.CASCADE, related_name='comment_issue'
    )
    created_time = models.DateTimeField(auto_now_add=True)
