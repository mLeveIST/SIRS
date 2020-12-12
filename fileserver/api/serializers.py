from rest_framework import serializers

from .models import File, Key

from fileserver import utils


class PGPKeyField(serializers.Field):
    def to_representation(self, evalue):
        return utils.bytes_to_string(evalue)

    def to_internal_value(self, data):
        return utils.string_to_bytes(data)


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['file']


class FileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'file']

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.file.name.split('/')[-1],
            'size': instance.file.size
        }


class KeySerializer(serializers.ModelSerializer):
    key = PGPKeyField()

    class Meta:
        model = Key
        fields = ['file_id', 'user_id', 'key']


class KeyValueSerializer(serializers.ModelSerializer):
    key = PGPKeyField()

    class Meta:
        model = Key
        fields = ['key']


class DataSerializer(serializers.ModelSerializer):
    keys = KeySerializer(source='key_set', many=True)

    class Meta:
        model = File
        fields = ['id', 'file', 'keys']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['keys'] = sorted(data['keys'], key=lambda key: key['user_id'])
        return data

