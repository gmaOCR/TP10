from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractUser


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        if not first_name:
            raise ValueError('Users must have a first_name')

        if not last_name:
            raise ValueError('Users must have a last_name')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        if not first_name:
            raise ValueError('Users must have a first_name')

        if not last_name:
            raise ValueError('Users must have a last_name')

        user = self.create_user(
            email,
            first_name,
            last_name,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        # user.set_password(password)
        user.save()
        return user


class User(AbstractUser):
    """Classe contenant tous les champs et méthodes de User par défaut.
    Args:
        AbstractUser (class): classe par défaut django pour un user
    """

    email = models.EmailField(unique=True)
    username = None

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

