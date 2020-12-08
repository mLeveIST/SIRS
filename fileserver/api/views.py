from django.conf import settings
from django.core import management
from django.db import transaction
from django.http import FileResponse, HttpResponse

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

            key = Key.objects.get(file_id=file_id , user_id=user['user_id'])
            key_serial = KeySerializer(
                instance=key,
                data={'key': user['key']},
                partial=True)

            key_serial.is_valid(raise_exception=True)
            key_serial.save()

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_file(request, file_id, user_id):
    pass
    # # File download
    # file = File.objects.get(id=file_id)
    # key = Key.objects.get(user_id=user_id, file=file_id)
    # path = os.path.join(settings.SENDFILE_ROOT, file.file.path)
    # response = sendfile(request, path, attachment=True)
    # response['key'] = KeySerializer(key).data['key']
    # return response


@api_view(['GET'])
def get_files(request, user_id):
    pass
    # # Listing of user files
    # files = File.objects.filter(key__user_id=user_id)
    # serial = FileDetailSerializer(files, many=True)
    # return Response(serial.data, status.HTTP_200_OK)


# --------------------------------------- #
# Services to be called by Backup Servers #
# --------------------------------------- #

@api_view(['GET'])
def recover_data(request, bserver_id):
    pass
    # r = requests.get(f"http://localhost:800{bserver_id}/api/files/")  # TEMP

    # if r.status_code < 200 or r.status_code >= 300:
    #     return Response(status=r.status_code)

    # if utils.empty_directory('sharedfiles'):
    #     return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)  # TEMP

    # utils.remove_files('files')
    # management.call_command('flush', verbosity=0, interactive=False)

    # utils.backup_cmd('mediarestore')
    # utils.backup_cmd('dbrestore')

    # return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def get_data(request):
    pass
    # # TODO only backup servers can call this function

    # utils.backup_cmd('mediabackup', '--clean')
    # utils.backup_cmd('dbbackup', '--clean')

    # file_data = DataSerializer(File.objects.all(), many=True)

    # return Response(file_data.data, status=status.HTTP_200_OK)

