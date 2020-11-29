import requests

from pathlib import Path

from django.core import management

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from backupserver import utils
from .models import File, Key
from .serializers import DataSerializer

# TEMP
FILESERVER_URL = "http://localhost:8001/api/"


# ------------------------------------ #
# Services to be called by Logs Server #
# ------------------------------------ #

@api_view(['GET'])
def backup_data(request):
	# TODO only logs server can call this function
	
	r = requests.get(f"{FILESERVER_URL}files/") # TEMP

	if r.status_code < 200 or r.status_code >= 300:
		return Response(status=r.status_code)

	if utils.empty_temp_files():
		return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR) # TEMP

	utils.backup_cmd('mediarestore', '--input-path=temp/filestemp.tar')
	utils.backup_cmd('dbrestore', '--input-path=temp/dbtemp.dump')

	files_data = DataSerializer(File.objects.all(), many=True)

	system_status = utils.check_integrity(request.data, files_data)

	if system_status:
		utils.backup_cmd('mediabackup', '--clean')
		utils.backup_cmd('dbbackup', '--clean')

	utils.remove_files('files')
	management.call_command('flush', verbosity=0, interactive=False)

	return Response({'system_status': system_status}, status=status.HTTP_200_OK)


# ------------------------------------- #
# Services to be called by Files Server #
# ------------------------------------- #

@api_view(['GET'])
def get_data(request):
	# TODO only files server can call this function

	# These 4 lines could be also be a 'cp'
	utils.backup_cmd('mediarestore')
	utils.backup_cmd('dbrestore')

	utils.backup_cmd('mediabackup', '--output-path=temp/filestemp.tar')
	utils.backup_cmd('dbbackup', '--output-path=temp/dbtemp.dump')

	utils.remove_files('files')
	management.call_command('flush', verbosity=0, interactive=False)

	file_data = DataSerializer(File.objects.all(), many=True)

	return Response(file_data.data, status=status.HTTP_200_OK)















