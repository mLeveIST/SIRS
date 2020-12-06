from django.db import models


class File(models.Model):
    file = models.FileField(upload_to='%Y%m%d%H%M%S/')


class Key(models.Model):
    user_id = models.IntegerField()
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    key = models.BinaryField()
