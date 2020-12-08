from datetime import datetime
from json import loads

from django.db import transaction
from django.db.models import Max
from django.http import HttpResponse

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from logserver import utils

from .models import User, Log
from .requests import upload_file_to, update_file_to, get_files_from, get_file_from
from .validators import is_valid_upload_file_request, is_valid_update_file_request, is_valid_access
from .serializers import RegisterSerializer, PubKeySerializer, LogSerializer

import requests

FILESERVER_URL = "http://localhost:8001/api"


# ---------------------------------------- #
# Services to be called by Client Machines #
# ---------------------------------------- #

@api_view(['POST'])
def register_user(request):
    serial = RegisterSerializer(data=request.data)

    serial.is_valid(raise_exception=True)
    user = serial.save()

    token = Token.objects.get(user=user)

    return Response({'token': token.key}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request, file_id):

    error_msg = {}

    error_code = is_valid_access(request.user.id, file_id, error_msg)
    if error_code:
        return Response(error_msg, error_code)

    users = User.objects.filter(pk__in=contributors)

    serial = PubKeySerializer(users, many=True)
    return Response(serial.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request, username):

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {'username': [f"User '{username}' does not exist."]}, 
            status=status.HTTP_404_NOT_FOUND)

    serial = PubKeySerializer(user)
    return Response(serial.data, status=status.HTTP_200_OK)


def upload_file(request):

    data = loads(request.data['json'])
    users = []

    is_valid_upload_file_request(request, data, users)

    signature = data.pop('signature')
    response = upload_file_to(FILESERVER_URL, request, data, users)

    if response.status_code != 201:
        return Response(response.content, status=response.status_code)

    response_data = response.json()

    with transaction.atomic():
        timestamp = datetime.now()
        for user in users:
            log_serial = LogSerializer(data={
                'user_id': user.id,
                'file_id': response_data['file_id'],
                'version': 0,
                'timestamp': timestamp})

            log_serial.is_valid(raise_exception=True)
            log_serial.save()

        log_serial = LogSerializer(data={
            'user_id': request.user.id,
            'file_id': response_data['file_id'],
            'version': 1,
            'timestamp': datetime.now(),
            'signature': signature})

        log_serial.is_valid(raise_exception=True)
        log_serial.save()

    return Response({'file_id': response_data['file_id']}, status=response.status_code)


def update_file(request, file_id):
    
    data = loads(request.data['json'])
    users = []

    is_valid_update_file_request(request, data, file_id, users)

    version = data.pop('version')
    signature = data.pop('signature')
    response = update_file_to(FILESERVER_URL, file_id, request, data, users)

    if response.status_code != 204:
        return Response(response.content, status=response.status_code)

    log_serial = LogSerializer(data={
        'user_id': request.user.id,
        'file_id': file_id,
        'version': version,
        'timestamp': datetime.now(),
        'signature': signature})

    log_serial.is_valid(raise_exception=True)
    log_serial.save()

    return Response(status=response.status_code)


def get_files(request):

    response = get_files_from(FILESERVER_URL, request.user.id)

    if response.status_code != 200:
        return Response(response.content, status=response.status_code)

    return Response(response.json(), status=response.status_code)


def get_file(request, file_id):

    user = request.user
    error_msg = {}

    error_code = is_valid_access(user.id, file_id, error_msg)
    if error_code:
        return Response(error_msg, error_code)

    response = get_file_from(FILESERVER_URL, user.id, file_id)

    if response.status_code != 200:
        return Response(response.content, status=response.status_code)

    # Adding version header to response
    response.headers['version'] = Log.objects \
        .filter(file_id=file_id) \
        .aggregate(version=Max('version'))['version']

    httpResponse = HttpResponse(
        content=response.content,
        status=response.status_code
    )

    for header, value in response.headers.items():
        httpResponse[header] = value

    return httpResponse


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def files_detail(request):
    
    if request.method == 'GET':
        return get_files(request)
    elif request.method == 'POST':
        return upload_file(request)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def file_detail(request, file_id):

    if request.method == 'GET':
        return get_file(request, file_id)
    elif request.method == 'PUT':
        return update_file(request, file_id)


def report_file(request):
    pass
