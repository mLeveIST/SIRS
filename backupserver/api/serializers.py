from rest_framework import serializers

from .models import File, Key

class KeySerializer(serializers.ModelSerializer):
	class Meta:
		model = Key
		fields = ['file', 'user', 'evalue']

class DataSerializer(serializers.ModelSerializer):
	keys = KeySerializer(source='key_set', many=True, read_only=True)

	class Meta:
		model = File
		fields = ['id', 'edata', 'keys']

class FileSerializer(serializers.ModelSerializer):
	class Meta:
		model = File
		fields = ['id', 'edata']