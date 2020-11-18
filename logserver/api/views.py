import requests
from datetime import datetime

from rest_framework import status
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from .models import User
from .serializers import RegisterSerializer, LogSerializer

FILESERVER_URL = "http://localhost:8001/api/"

# Create your views here.


@api_view(['POST'])
def upload_file(request):
    user = request.user
    if not user.is_authenticated:
        raise PermissionDenied("You need to be authenticated to upload a file")

    r = requests.post(FILESERVER_URL + "user/{0}/file".format(user.id),
                      files=request.FILES, data={'key': request.data["key"]})

    if r.status_code < 200 or r.status_code >= 300:
        return Response(r.content, status=r.status_code)

    log_data = {
        'file_id': r.json()['file_id'],
        'user': user,
        'ts': datetime.now(),
        'sign': request.data['sign']
    }
    log_serial = LogSerializer(data=log_data)
    if not log_serial.is_valid():
        return Response(log_serial.errors, status=status.HTTP_400_BAD_REQUEST)
    log = log_serial.save()

    return Response(status=status.HTTP_201_CREATED)


# Auth views


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
