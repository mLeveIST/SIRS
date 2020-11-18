from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import FileSerializer, KeySerializer


@api_view(['GET'])
def get_files():
    return


@api_view(['POST'])
def upload_file(request, user_id):
    file_serial = FileSerializer(data={'file': request.FILES})
    if not file_serial.is_valid():
        return Response(file_serial.errors, status=status.HTTP_400_BAD_REQUEST)
    file = file_serial.save()

    key_data = {'owner_id': user_id, 'value': request.data['key'], 'file': file}
    key_serial = KeySerializer(data=key_data)
    if not key_serial.is_valid():
        return Response(key_serial.errors, status=status.HTTP_400_BAD_REQUEST)
    key = key_serial.save()

    return Response({'file_id': file.id}, status=status.HTTP_201_CREATED)
