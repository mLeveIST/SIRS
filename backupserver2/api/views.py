import requests

from pathlib import Path

from django.core import management

from rest_framework import status
from json import loads

from rest_framework.decorators import api_view
from rest_framework.response import Response

from backupserver import utils

from .models import File, Key
from .serializers import DataSerializer
from .validators import check_integrity


FILESERVER_URL = "https://file/api"  # For Prod
#FILESERVER_URL = "http://localhost:8001/api"  # For dev

location = "/var/repo/backupserver/" # For Prod
#location = "" #For dev


# ------------------------------------ #
# Services to be called by Logs Server #
# ------------------------------------ #

@api_view(['POST'])
def backup_data(request):

	logs_data = loads(request.data['json'])

	files_data = requests.get(f"{FILESERVER_URL}/data/")

	if files_data.status_code != 200:
		return Response(status=files_data.status_code)

	if utils.empty_directory(location + 'sharedfiles'):
		return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	utils.backup_cmd('mediarestore')
	utils.backup_cmd('dbrestore')

	system_status = check_integrity(files_data.json(), logs_data)

	if system_status:
		utils.backup_cmd('mediabackup', '--output-path=' + location + 'backups/files_backup.tar.gz')
		utils.backup_cmd('dbbackup', '--output-path=' + location + 'backups/db_backup.dump')

	utils.remove_files(location + 'files')
	management.call_command('flush', verbosity=0, interactive=False)

	return Response({'system_status': system_status}, status=status.HTTP_200_OK)


# ------------------------------------- #
# Services to be called by Files Server #
# ------------------------------------- #

@api_view(['GET'])
def get_data(request):
	utils.backup_cmd('mediarestore', '--input-path=' + location + 'backups/files_backup.tar.gz')
	utils.backup_cmd('dbrestore', '--input-path=' + location + 'backups/db_backup.dump')

	utils.backup_cmd('mediabackup', '--clean')
	utils.backup_cmd('dbbackup', '--clean')

	utils.remove_files(location + 'files')
	management.call_command('flush', verbosity=0, interactive=False)

	file_data = DataSerializer(File.objects.all(), many=True)

	return Response(file_data.data, status=status.HTTP_200_OK)
