from datetime import datetime

from django.db import transaction

from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

import json
import requests


def upload_file_to(url, request, data, users):

	request.FILES['efile'].open() # seek(0)

	for index, contributor in enumerate(data['contributors']):
		contributor.pop('username')
		contributor['user_id'] = users[index].id

	jdata = {'json': json.dumps(data)}

	return requests.post(f'{url}/files/', files=request.FILES, data=jdata)


def update_file_to(url, file_id, request, data, users):

	request.FILES['efile'].open() # seek(0)

	for index, contributor in enumerate(data['contributors']):
		contributor.pop('username')
		contributor['user_id'] = users[index].id

	jdata = {'json': json.dumps(data)}

	return requests.put(f'{url}/files/{file_id}/', files=request.FILES, data=jdata)