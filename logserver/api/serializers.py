from rest_framework import serializers
from .models import User, Log

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
    pub_key = RSAPublicKeyField()

    class Meta:
        model = User
        fields = ['username', 'password', 'pub_key']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self):
        user = User(
            username=self.validated_data['username'],
            pub_key=self.validated_data['pub_key'],
        )
        user.set_password(self.validated_data['password'])
        user.save()
        return user


class PubKeySerializer(serializers.ModelSerializer):
    pub_key = RSAPublicKeyField()

    class Meta:
        model = User
        fields = ['username', 'pub_key']


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ['user_id', 'file_id', 'version', 'timestamp', 'signature']

