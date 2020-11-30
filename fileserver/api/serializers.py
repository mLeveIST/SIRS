from rest_framework import serializers
from .models import File, Key

from cryptography.hazmat.primitives import serialization


class PGPKeyField(serializers.Field):
    def to_representation(self, value):
        return value.decode()

    def to_internal_value(self, data):
        return data.encode()


class UploadFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['file']


class KeySerializer(serializers.ModelSerializer):
    key = PGPKeyField()

    class Meta:
        model = Key
        fields = ['user_id', 'key', 'file']


class DownloadFileSerializer(serializers.ModelSerializer):
    key = serializers.IntegerField()

    class Meta:
        model = File
        fields = ['file', 'key']


class FileIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id']
