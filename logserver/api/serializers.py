from rest_framework import serializers
from .models import User, Log


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def save(self):
        user = User(
            username=self.validated_data['username'],
            pubkey=self.validated_data['pubkey'],
        )
        user.set_password(self.validated_data['password'])
        user.save()
        return user


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ['file_id', 'user', 'ts', 'sign']


class PubkeySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pubkey']
