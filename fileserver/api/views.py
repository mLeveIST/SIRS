import os
from sendfile import sendfile

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import FileResponse, HttpResponse
from django.conf import settings

from .models import File, Key
from .serializers import FileContentSerializer, FileDetailSerializer, KeySerializer


@api_view(['GET', 'PUT'])
def file_detail(request, user_id, file_id):
    # Includes get a specific file of a specific user and update a file that already exists
    if request.method == 'GET':
        # File download
        file = File.objects.get(id=file_id)
        key = Key.objects.get(user_id=user_id, file=file_id)
        path = os.path.join(settings.SENDFILE_ROOT, file.file.path)
        response = sendfile(request, path, attachment=True)
        response['key'] = KeySerializer(key).data['key']
        return response

    elif request.method == 'PUT':
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


@api_view(['GET', 'POST'])
def file_list(request, user_id):
    # Includes get all files of a specific user and a upload of a file
    # At this time, no GET of all files is done, just upload file (POST)

    if request.method == 'GET':
        files = File.objects.filter(key__user_id=user_id)
        serial = FileDetailSerializer(files, many=True)
        return Response(serial.data, status.HTTP_200_OK)

    elif request.method == 'POST':
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
