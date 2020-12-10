from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token


class UserManager(BaseUserManager):
    def create_user(self, username, pubkey, password=None):
        if not username:
            raise ValueError("Users must have a username!")
        if not pubkey:
            raise ValueError("Users must have an associated public key!")

        user = self.model(username=username, pubkey=pubkey)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(
            username=username,
            pubkey=b'adminpubkey',
            password=password
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=30, unique=True)
    pubkey = models.BinaryField(unique=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'

    objects = UserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Log(models.Model):
    user_id = models.ForeignKey(User, db_column='user_id', on_delete=models.CASCADE)
    file_id = models.IntegerField()
    version = models.PositiveIntegerField()
    timestamp = models.DateTimeField()
    signature = models.CharField(max_length=344, blank=True)


class Backup(models.Model):
    timestamp = models.DateTimeField()
    successful = models.BooleanField()
