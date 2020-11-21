from rest_framework import serializers

from core.models import File, Key

class FileSerializer(serializers.ModelSerializer):
	class Meta:
		model = File
		fields = ['id', 'edata']

class KeySerializer(serializers.ModelSerializer):
	class Meta:
		model = Key
		fields = ['id', 'user', 'file', 'evalue']

class DataSerializer(serializers.Serializer):
	pass


