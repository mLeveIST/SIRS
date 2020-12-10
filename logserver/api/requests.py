from datetime import datetime

from django.db import transaction

from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

import json
import requests


def upload_file_to(url, request, data, users):
	request.FILES['file'].open() # seek(0)

	for index, contributor in enumerate(data['contributors']):
		contributor.pop('username')
		contributor['user_id'] = users[index].id

	jdata = {'json': json.dumps(data)}

	return requests.post(f'{url}/files/', files=request.FILES, data=jdata)


def update_file_to(url, file_id, request, data, users):
	request.FILES['file'].open() # seek(0)

	for index, contributor in enumerate(data['contributors']):
		contributor.pop('username')
		contributor['user_id'] = users[index].id

	jdata = {'json': json.dumps(data)}

	return requests.put(f'{url}/files/{file_id}/', files=request.FILES, data=jdata)


def list_files_from(url, user_id):
	return requests.get(f'{url}/users/{user_id}/files/')


def download_file_from(url, user_id, file_id):
	return requests.get(f'{url}/users/{user_id}/files/{file_id}/')


def get_file_data_from(url, file_id):
	return requests.get(f'{url}/data/{file_id}/')


def backup_data_to(urls, data):
	responses = []
	jdata = {'json': json.dumps(data)}

	for url in urls:
		response = requests.post(f'{url}/data/backup/', data=jdata)
		responses.append(response)

	return responses


def recover_data_from(url, buserver_id):
	return requests.get(f'{url}/data/recover/{buserver_id}/')










