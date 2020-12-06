import os
import requests
from sendfile import sendfile

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.http import FileResponse, HttpResponse
from django.conf import settings
from django.core import management

from fileserver import utils
from .models import File, Key
from .serializers import FileContentSerializer, FileDetailSerializer, KeySerializer

# ------------------------------------ #
# Services to be called by Logs Server #
# ------------------------------------ #


@api_view(['GET', 'PUT'])
def file_detail(request, user_id, file_id):
    # Includes get a specific file of a specific user and update a file that already exists
    if request.method == 'GET':
        return get_file(request, user_id, file_id)
    elif request.method == 'PUT':
        return update_file(request, user_id, file_id)


@api_view(['GET', 'POST'])
def file_list(request, user_id):
    # Includes get all files of a specific user and a upload of a file
    # At this time, no GET of all files is done, just upload file (POST)

    if request.method == 'GET':
        return list_files(request, user_id)
    elif request.method == 'POST':
        return upload_file(request, user_id)


def get_file(request, user_id, file_id):
    # File download
    file = File.objects.get(id=file_id)
    key = Key.objects.get(user_id=user_id, file=file_id)
    path = os.path.join(settings.SENDFILE_ROOT, file.file.path)
    response = sendfile(request, path, attachment=True)
    response['key'] = KeySerializer(key).data['key']
    return response


def update_file(request, user_id, file_id):
    # File update
    file = File.objects.get(id=file_id)
    file_serial = FileContentSerializer(instance=file, data=request.FILES)
    if not file_serial.is_valid():
        return Response(file_serial.errors, status=status.HTTP_400_BAD_REQUEST)
    file = file_serial.save()
    # Missing delete file from media

    key = Key.objects.get(user_id=user_id, file=file_id)
    key_serial = KeySerializer(instance=key, data={'key': request.data['key']}, partial=True)
    if not key_serial.is_valid():
        return Response(key_serial.errors, status=status.HTTP_400_BAD_REQUEST)
    key = key_serial.save()

    return Response(status=status.HTTP_204_NO_CONTENT)


def upload_file(request, user_id):
    # File upload
    file_serial = FileContentSerializer(data=request.FILES)
    if not file_serial.is_valid():
        return Response(file_serial.errors, status=status.HTTP_400_BAD_REQUEST)
    file = file_serial.save()

    key_data = {'user_id': user_id, 'key': request.data['key'], 'file': file.id}
    key_serial = KeySerializer(data=key_data)
    if not key_serial.is_valid():
        return Response(key_serial.errors, status=status.HTTP_400_BAD_REQUEST)
    key = key_serial.save()

    return Response({'file_id': file.id}, status=status.HTTP_201_CREATED)


def list_files(request, user_id):
    # Listing of user files
    files = File.objects.filter(key__user_id=user_id)
    serial = FileDetailSerializer(files, many=True)
    return Response(serial.data, status.HTTP_200_OK)


@api_view(['GET'])
def recover_data(request, server_id):
    r = requests.get(f"http://localhost:800{server_id}/api/files/")  # TEMP

    if r.status_code < 200 or r.status_code >= 300:
        return Response(status=r.status_code)

    if utils.empty_directory('sharedfiles'):
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)  # TEMP

    utils.remove_files('files')
    management.call_command('flush', verbosity=0, interactive=False)

    utils.backup_cmd('mediarestore')
    utils.backup_cmd('dbrestore')

    return Response(status=status.HTTP_200_OK)

# --------------------------------------- #
# Services to be called by Backup Servers #
# --------------------------------------- #


@api_view(['GET'])
def get_data(request):
    # TODO only backup servers can call this function

    utils.backup_cmd('mediabackup', '--clean')
    utils.backup_cmd('dbbackup', '--clean')

    file_data = DataSerializer(File.objects.all(), many=True)

    return Response(file_data.data, status=status.HTTP_200_OK)
