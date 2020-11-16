from django.db import models


# For user and auth
from fileserver import settings
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework.authtoken.models import Token

# Other models


class File(models.Model):
    path = models.FileField()


class Key(models.Model):
    owner_id = models.IntegerField()
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    value = models.BinaryField()
