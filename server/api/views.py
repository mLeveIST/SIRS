from rest_framework import status
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from .models import User
from .serializers import RegisterSerializer


@api_view(['POST'])
def register(request):
    data = {}
    serial = RegisterSerializer(data=request.data)
    if not serial.is_valid():
        return Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)
    user = serial.save()
    token = Token.objects.get(user=user)

    data['response'] = 'successfully registered a new user'
    data['email'] = user.email
    data['token'] = token.key
    return Response(data, status=status.HTTP_201_CREATED)


class LoginClass(ObtainAuthToken):
    def post(self, request):
        data = {'password': request.data['password']}

        if request.data.get('email'):
            data['username'] = request.data['email']
        elif request.data.get('phone'):
            data['username'] = User.objects.get(
                phone=request.data.get('phone')).email
        else:
            return Response({'response': 'error: please introduce a valid email or a phone'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(
            data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
