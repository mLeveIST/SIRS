import requests
from logserver import utils
from datetime import datetime

from rest_framework import status
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from .models import User
from .serializers import RegisterSerializer, LogSerializer, PubkeySerializer

FILESERVER_URL = "http://localhost:8001/api/"
#FILESERVER_URL = "http://file/api/"
# Create your views here.


@api_view(['GET'])
def get_pubkey(request, username):
    user = User.objects.get(username=username)
    serial = PubkeySerializer(user)
    return Response(serial.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
def file_details(request, file_id):
    # Includes get a specific file and update a file that already exists
    # Download or Update a specific file
    user = utils.authenticated_user(request)
    url = FILESERVER_URL + "file/{}/user/{}/".format(user.id, file_id)

    if request.method == 'GET':
        r = requests.get(url)
    elif request.method == 'PUT':
        r = requests.put(url, files=request.FILES, data={'key': request.data["key"]})

    if r.status_code < 200 or r.status_code >= 300:
        return Response(r.content, status=r.status_code)

    if request.method == 'PUT':
        log_data = {
            'file_id': file_id,
            'user': user.id,
            'ts': datetime.now(),
            'sign': request.data['sign']
        }
        log_serial = LogSerializer(data=log_data)
        if not log_serial.is_valid():
            return Response(log_serial.errors, status=status.HTTP_400_BAD_REQUEST)
        log = log_serial.save()

    return utils.requests_to_django(r)


@api_view(['GET', 'POST'])
def file_list(request):
    user = utils.authenticated_user(request)
    url = FILESERVER_URL + "file/user/{}/".format(user.id)

    if request.method == 'GET':
        return utils.requests_to_django(request.get(url))

    elif request.method == 'POST':
        r = requests.post(url, files=request.FILES, data={'key': request.data["key"]})

        if r.status_code < 200 or r.status_code >= 300:
            return Response(r.content, status=r.status_code)

        log_data = {
            'file_id': r.json()['file_id'],
            'user': user.id,
            'ts': datetime.now(),
            'sign': request.data['sign']
        }
        log_serial = LogSerializer(data=log_data)
        if not log_serial.is_valid():
            return Response(log_serial.errors, status=status.HTTP_400_BAD_REQUEST)
        log = log_serial.save()

        return Response({'file_id': log.file_id}, status=status.HTTP_201_CREATED)


# Auth views


@api_view(['POST'])
def register(request):
    serial = RegisterSerializer(data=request.data)
    if not serial.is_valid():
        return Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)
    user = serial.save()
    token = Token.objects.get(user=user)

    return Response({'token': token.key}, status=status.HTTP_201_CREATED)


class LoginClass(ObtainAuthToken):
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
