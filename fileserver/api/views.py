from django.conf import settings
from django.core import management
from django.db import transaction
from django.http import FileResponse

from json import loads

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from sendfile import sendfile

from fileserver import utils
from .models import *
from .serializers import *

import os
import requests

location = "/var/repo/fileserver/" #For prod
#location = "" #For dev

# ------------------------------------ #
# Services to be called by Logs Server #
# ------------------------------------ #

@api_view(['POST'])
def upload_file(request):

    data = loads(request.data['json'])
    file_id = 0

    with transaction.atomic():
        file_serial = FileSerializer(data=request.FILES)

        file_serial.is_valid(raise_exception=True)
        file = file_serial.save()

        file_id = file.id

        for user in data['contributors']:

            key_serial = KeySerializer(data={
                'user_id': user['user_id'],
                'file_id': file_id,
                'key': user['key']
            })

            key_serial.is_valid(raise_exception=True)
            key_serial.save()

    return Response({'file_id': file_id}, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def update_file(request, file_id):

    data = loads(request.data['json'])

    with transaction.atomic():
        file = File.objects.get(id=file_id)
        file_serial = FileSerializer(instance=file, data=request.FILES)

        file_serial.is_valid(raise_exception=True)
        file = file_serial.save()

        for user in data['contributors']:

            key = Key.objects.get(file_id=file_id, user_id=user['user_id'])
            key_serial = KeySerializer(
                instance=key,
                data={'key': user['key']},
                partial=True)

            key_serial.is_valid(raise_exception=True)
            key_serial.save()

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def list_files(request, user_id):

    files = File.objects.filter(key__user_id=user_id)
    serial = FileInfoSerializer(files, many=True)
    return Response(serial.data, status.HTTP_200_OK)


@api_view(['GET'])
def download_file(request, user_id, file_id):

    file = File.objects.get(id=file_id).file
    key = Key.objects.get(user_id=user_id, file_id=file_id)

    file.open()  # seek(0)

    path = os.path.join(settings.SENDFILE_ROOT, file.path)
    response = sendfile(request, path, attachment=True)
    response['key'] = KeyValueSerializer(key).data['key']

    return response


@api_view(['GET'])
def get_file_data(request, file_id):
    serial = DataSerializer(File.objects.get(id=file_id))
    return Response(serial.data, status=status.HTTP_200_OK)

# --------------------------------------- #
# Services to be called by Backup Servers #
# --------------------------------------- #


@api_view(['GET'])
def recover_data(request, bserver_id):
    response = requests.get(f"https://bs{bserver_id}/api/data/") # For prod
    #response = requests.get(f"http://localhost:800{bserver_id}/api/data/")  # For dev

    if response.status_code != 200:
        return Response(status=response.status_code)

    if utils.empty_directory(location + 'sharedfiles'):
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    utils.remove_files(location + 'files')
    management.call_command('flush', verbosity=0, interactive=False)

    utils.backup_cmd('mediarestore')
    utils.backup_cmd('dbrestore')

    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def get_data(request):
    utils.backup_cmd('mediabackup', '--clean')
    utils.backup_cmd('dbbackup', '--clean')

    serial = DataSerializer(File.objects.all(), many=True)

    return Response(serial.data, status=status.HTTP_200_OK)
