import os
from sendfile import sendfile

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import FileResponse, HttpResponse
from django.conf import settings

from .models import File, Key
from .serializers import FileSerializer, KeySerializer, GetFileSerializer


@api_view(['GET'])
def download_file(request, user_id, file_id):
    file = File.objects.get(id=file_id)
    key = Key.objects.get(user_id=user_id, file=file_id)
    path = os.path.join(settings.SENDFILE_ROOT, file.file.path)
    response = sendfile(request, path, attachment=True)
    response['key'] = key.value
    return response


@api_view(['POST'])
def upload_file(request, user_id):
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
