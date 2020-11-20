from rest_framework import serializers
from .models import File, Key


class UploadFileSerializer(serializers.Serializer):
    file = serializers.FileField()
    key = serializers
    user_id = serializers.IntegerField()


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['file']


class KeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = ['owner_id', 'value', 'file']
