from rest_framework import serializers
from .models import File, Key


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['efile']


class KeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = ['file_id', 'user_id', 'evalue']


class GetFileSerializer(serializers.ModelSerializer):
    key = serializers.IntegerField()

    class Meta:
        model = File
        fields = ['efile', 'key']


class DataSerializer(serializers.ModelSerializer):
    keys = KeySerializer(source='key_set', many=True)

    class Meta:
        model = File
        fields = ['id', 'efile', 'keys']