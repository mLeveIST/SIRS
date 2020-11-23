import os
from sendfile import sendfile

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import FileResponse, HttpResponse
from django.conf import settings

from fileserver import utils
from .models import File, Key
from .serializers import FileSerializer, KeySerializer, GetFileSerializer

# ------------------------------------ #
# Services to be called by Logs Server #
# ------------------------------------ #


@api_view(['GET', 'PUT'])
def file_detail(request, user_id, file_id):
    # Includes get a specific file of a specific user and update a file that already exists
    if request.method == 'GET':
        get_file(request, user_id, file_id)
    elif request.method == 'PUT':
        upload_file(request, user_id, file_id)


def get_file(request, user_id, file_id):
    # File download
    file = File.objects.get(id=file_id)
    key = Key.objects.get(user_id=user_id, file=file_id)
    path = os.path.join(settings.SENDFILE_ROOT, file.file.path)
    response = sendfile(request, path, attachment=True)
    response['key'] = key.value
    return response


def upload_file(request, user_id, file_id):
    # File update
    file = File.objects.get(id=file_id)
    file_serial = FileSerializer(instance=file, data=request.FILES)
    if not file_serial.is_valid():
        return Response(file_serial.errors, status=status.HTTP_400_BAD_REQUEST)
    file = file_serial.save()
    # Missing delete file from media

    key = Key.objects.get(user_id=user_id, file=file_id)
    key_serial = KeySerializer(instance=key, data={'value': request.data['key']}, partial=True)
    if not key_serial.is_valid():
        return Response(key_serial.errors, status=status.HTTP_400_BAD_REQUEST)
    key = key_serial.save()

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def file_list(request, user_id):
    # Includes get all files of a specific user and a upload of a file
    # At this time, no GET of all files is done, just upload file (POST)

    if request.method == 'POST':
        file_serial = FileSerializer(data=request.FILES)
        if not file_serial.is_valid():
            return Response(file_serial.errors, status=status.HTTP_400_BAD_REQUEST)
        file = file_serial.save()

        key_data = {'user_id': user_id, 'value': request.data['key'], 'file': file.id}
        key_serial = KeySerializer(data=key_data)
        if not key_serial.is_valid():
            return Response(key_serial.errors, status=status.HTTP_400_BAD_REQUEST)
        key = key_serial.save()

        return Response({'file_id': file.id}, status=status.HTTP_201_CREATED)


# --------------------------------------- #
# Services to be called by Backup Servers #
# --------------------------------------- #


@api_view(['GET'])
def get_data(request):
    # TODO only backup servers can call this function

    #utils.backup_cmd('mediabackup')
    #utils.backup_cmd('dbbackup')

    return Response(status=status.HTTP_200_OK)










