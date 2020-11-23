from rest_framework import serializers
from .models import File, Key


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['file']


class KeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = ['user_id', 'value', 'file']


class GetFileSerializer(serializers.ModelSerializer):
    key = serializers.IntegerField()

    class Meta:
        model = File
        fields = ['file', 'key']
