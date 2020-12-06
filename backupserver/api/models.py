from django.db import models


class File(models.Model):
	efile = models.FileField(upload_to='%Y%m%d%H%M%S/')


class Key(models.Model):
	user_id = models.PositiveIntegerField()
	file_id = models.ForeignKey(File, on_delete=models.CASCADE)
	evalue = models.CharField(max_length=300)