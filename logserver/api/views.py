from datetime import datetime
from json import loads

from django.db import transaction

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from logserver import utils

from .models import *
from .requests import *
from .serializers import *

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
def get_users(request, file_id): # TODO - If file_id does not exist, return 404

    contributors = Log.objects \
        .filter(file_id=file_id, version=0) \
        .values_list('user_id', flat=True)

    users = User.objects.filter(pk__in=list(contributors))

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

    utils.is_valid_upload_file_request(request, data, users)

    signature = data.pop('signature')
    response = upload_file_to(FILESERVER_URL, request, data, users)

    if response.status_code != 201:
        return Response(response.content, status=response.status_code)

    response = response.json()

    with transaction.atomic():
        # Add initial logs for all contributors, to track who has access to the file
        timestamp = datetime.now()
        for user in users:
            log_serial = LogSerializer(data={
                'user_id': user.id,
                'file_id': response['file_id'],
                'version': 0,
                'timestamp': timestamp})

            log_serial.is_valid(raise_exception=True)
            log_serial.save()

        # Add log of file creation
        log_serial = LogSerializer(data={
            'user_id': request.user.id,
            'file_id': response['file_id'],
            'version': 1,
            'timestamp': datetime.now(),
            'signature': signature})

        log_serial.is_valid(raise_exception=True)
        log_serial.save()

    return Response({'file_id': response['file_id']}, status=status.HTTP_201_CREATED)


def update_file(request, file_id):
    
    data = loads(request.data['json'])
    users = []

    utils.is_valid_update_file_request(request, data, file_id, users)

    print("valid")

    version = data.pop('version')
    signature = data.pop('signature')
    response = update_file_to(FILESERVER_URL, file_id, request, data, users)

    if response.status_code != 204:
        return Response(response.content, status=response.status_code)

    # Add log of file creation
    log_serial = LogSerializer(data={
        'user_id': request.user.id,
        'file_id': file_id,
        'version': version,
        'timestamp': datetime.now(),
        'signature': signature})

    log_serial.is_valid(raise_exception=True)
    log_serial.save()

    return Response(status=status.HTTP_204_NO_CONTENT)


def get_file(request, file_id):
    pass
    # user = utils.authenticated_user(request)
    # url = FILESERVER_URL + "files/{}/users/{}/".format(file_id, user.id)

    # r = requests.get(url)
    # if r.status_code < 200 or r.status_code >= 300:
    #     return Response(r.content, status=r.status_code)

    # return utils.requests_to_django(r)


def get_files(request):
    pass
    # user = utils.authenticated_user(request)
    # url = FILESERVER_URL + "files/users/{}/".format(user.id)

    # file_list = requests.get(url).json()
    # q = Log.objects.filter(file_id__in=[f['id'] for f in file_list]).values(
    #     'file_id').annotate(version=Max('version'))

    # for file in file_list:
    #     for log in q:
    #         if file['id'] == log['file_id']:
    #             file['version'] = log['version']

    # return Response(file_list, status=status.HTTP_200_OK)


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
