from rest_framework import serializers
from .models import File, Key
from fileserver import utils

import base64
from cryptography.hazmat.primitives import serialization

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


class DataSerializer(serializers.ModelSerializer):
    keys = KeySerializer(source='key_set', many=True)

    class Meta:
        model = File
        fields = ['id', 'efile', 'keys']


# WILL UPDATE WITH THIS LATER
#
# class PGPKeyField(serializers.Field):
#     def to_representation(self, value):
#         return utils.bytes_to_string(value)

#     def to_internal_value(self, data):
#         return utils.string_to_bytes(data)


# class FileContentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = File
#         fields = ['file']


# class KeySerializer(serializers.ModelSerializer):
#     key = PGPKeyField()

#     class Meta:
#         model = Key
#         fields = ['user_id', 'key', 'file']
#         extra_kwargs = {'user_id': {'write_only': True}, 'file': {'write_only': True}}


# class FileDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = File
#         fields = ['id', 'file']

#     def to_representation(self, instance):
#         return {
#             'id': instance.id,
#             'name': instance.file.name.split('/')[-1],
#             'size': instance.file.size
#         }
