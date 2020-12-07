from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator

from fileserver import utils
from django.conf import settings

class File(models.Model):
	efile = models.FileField(upload_to='%Y%m%d%H%M%S/')

	def delete(self, *args, **kwargs):
		self.efile.delete()
		super().delete(*args, **kwargs)

@receiver(pre_save, sender=File)
def file_update(sender, **kwargs):
	instance = kwargs['instance']

	if instance.id:
		file_path = str(File.objects.get(id=instance.id).efile).split('/')[0]
		utils.remove_files(f"files/{file_path}", remove_self=True)


class Key(models.Model):
	user_id = models.IntegerField(validators=[MinValueValidator(1)])
	file_id = models.ForeignKey(File, on_delete=models.CASCADE)
	evalue = models.CharField(max_length=360)
