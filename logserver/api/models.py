from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, username, pubkey, password=None):
        user = self.model(username=username, pubkey=pubkey)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(
            username=username,
            password=password,
            pubkey='this is a superuser key'
        )
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=64, unique=True)
    pubkey = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'

    objects = UserManager()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Log(models.Model):
    file_id = models.IntegerField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ts = models.DateTimeField()
    sign = models.CharField(max_length=64)
