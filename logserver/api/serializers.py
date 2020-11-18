from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def save(self):
        user = User(
            name=self.validated_data['username'],
        )
        user.set_password(self.validated_data['password'])
        user.save()
        return user
