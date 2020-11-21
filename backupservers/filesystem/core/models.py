from django.db import models

class File(models.Model):
	edata = models.FileField('Encrypted File Reference')

class Key(models.Model):
	file = models.ForeignKey(File, on_delete=models.CASCADE)
	user = models.PositiveIntegerField()
	evalue = models.CharField('Encrypted Key Value', max_length=100)

class BackupLog(models.Model):
	ts = models.DateTimeField('Last Backup Date', auto_now=True)
