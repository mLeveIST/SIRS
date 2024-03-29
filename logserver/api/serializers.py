from rest_framework import serializers
from .models import User, Log, Backup

from cryptography.hazmat.primitives import serialization


class RSAPublicKeyField(serializers.Field):
    def to_representation(self, value):
        key_serial = serialization.load_der_public_key(value)
        return key_serial.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.PKCS1).decode()

    def to_internal_value(self, data):
        key_serial = serialization.load_pem_public_key(data.encode())
        return key_serial.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.PKCS1)


class RegisterSerializer(serializers.ModelSerializer):
    pubkey = RSAPublicKeyField()

    class Meta:
        model = User
        fields = ['username', 'password', 'pubkey']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self):
        user = User(
            username=self.validated_data['username'],
            pubkey=self.validated_data['pubkey'],
        )
        user.set_password(self.validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    pubkey = RSAPublicKeyField()

    class Meta:
        model = User
        fields = ['username', 'pubkey']


class PubkeySerializer(serializers.ModelSerializer):
    pubkey = RSAPublicKeyField()

    class Meta:
        model = User
        fields = ['pubkey']


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ['user_id', 'file_id', 'version', 'timestamp', 'signature']


class BackupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Backup
        fields = ['timestamp', 'successful']


class DataSerializer(serializers.ModelSerializer):
    pubkey = RSAPublicKeyField(source='user_id.pubkey', read_only=True)

    class Meta:
        model = Log
        fields = ['file_id', 'user_id', 'version', 'signature', 'pubkey']
