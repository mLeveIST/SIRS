from django.db import models


# For user and auth
from fileserver import settings
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework.authtoken.models import Token
from django.core.files.storage import FileSystemStorage


class File(models.Model):
    file = models.FileField(upload_to='%Y%m%d%H%M%S/')


class Key(models.Model):
    user_id = models.IntegerField()
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    key = models.BinaryField()
