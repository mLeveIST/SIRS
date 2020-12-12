from datetime import datetime
from json import loads

from django.db import transaction
from django.db.models import Max, Q, F
from django.http import HttpResponse

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from logserver.utils import requests_to_django

from .models import User, Log, Backup
from .requests import upload_file_to, update_file_to, list_files_from, download_file_from, get_file_data_from, backup_data_to, recover_data_from
from .serializers import RegisterSerializer, UserSerializer, LogSerializer, DataSerializer, BackupSerializer
from .validators import is_valid_upload_file_request, is_valid_update_file_request, is_valid_access, is_valid_signature, validate_response


FILESERVER_URL = "https://file/api"  # For prod
BACKUPSERVER1_URL = "https://bs1/api"  # For prod
BACKUPSERVER2_URL = "https://bs2/api"  # For prod

FILESERVER_URL = "http://localhost:8001/api"  # For dev
# BACKUPSERVER1_URL = "http://localhost:8002/api" # For dev
# BACKUPSERVER2_URL = "http://localhost:8003/api" # For dev


# ---------------------------------------- #
# Services to be called by Client Machines #
# ---------------------------------------- #

class login_user(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        response = {'token': token.key}
        if user.is_staff:
            response['role'] = 'staff'

        return Response(response)


@api_view(['POST'])
def register_user(request):
    serial = RegisterSerializer(data=request.data)

    serial.is_valid(raise_exception=True)
    user = serial.save()

    token = Token.objects.get(user=user)

    return Response({'token': token.key}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_file_contributors(request, file_id):
    error_msg = {}

    contributors = list(Log.objects
                        .filter(file_id=file_id, version=0)
                        .values_list('user_id', flat=True)
                        .order_by('user_id'))

    error_code = is_valid_access(request.user.id, file_id, error_msg, contributors)
    if error_code:
        return Response(error_msg, error_code)

    users = User.objects.filter(pk__in=contributors)

    serial = UserSerializer(users, many=True)
    return Response(serial.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_pubkey(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {'username': [f"User '{username}' does not exist."]},
            status=status.HTTP_404_NOT_FOUND)

    serial = UserSerializer(user)
    return Response(serial.data, status=status.HTTP_200_OK)


def upload_file(request):
    data = loads(request.data['json'])
    users = []

    is_valid_upload_file_request(request, data, users)

    signature = data.pop('signature')
    response = upload_file_to(FILESERVER_URL, request, data, users)

    if not validate_response(response, raise_exception=False):
        return requests_to_django(response)

    response_data = response.json()

    with transaction.atomic():
        timestamp = datetime.now()
        for user in users:
            log_serial = LogSerializer(data={
                'user_id': user.id,
                'file_id': response_data['file_id'],
                'version': 0,
                'timestamp': timestamp})

            log_serial.is_valid(raise_exception=True)
            log_serial.save()

        log_serial = LogSerializer(data={
            'user_id': request.user.id,
            'file_id': response_data['file_id'],
            'version': 1,
            'timestamp': datetime.now(),
            'signature': signature})

        log_serial.is_valid(raise_exception=True)
        log_serial.save()

    return Response({'file_id': response_data['file_id']}, status=response.status_code)


def update_file(request, file_id):
    data = loads(request.data['json'])
    users = []

    is_valid_update_file_request(request, data, file_id, users)

    version = data.pop('version')
    signature = data.pop('signature')
    response = update_file_to(FILESERVER_URL, file_id, request, data, users)

    if not validate_response(response, raise_exception=False):
        return requests_to_django(response)

    log_serial = LogSerializer(data={
        'user_id': request.user.id,
        'file_id': file_id,
        'version': version,
        'timestamp': datetime.now(),
        'signature': signature})

    log_serial.is_valid(raise_exception=True)
    log_serial.save()

    return Response(status=response.status_code)


def list_files(request):
    response = list_files_from(FILESERVER_URL, request.user.id)

    if not validate_response(response, raise_exception=False):
        return requests_to_django(response)

    files = response.json()

    # Get latest log for each file
    file_ids = [f['id'] for f in files]
    q = Log.objects.filter(file_id__in=file_ids).values('file_id').annotate(max_version=Max('version')).order_by()
    q_filter = Q()
    for entry in q:
        q_filter |= (Q(file_id=entry['file_id']) & Q(version=entry['max_version']))

    latest_file_logs = Log.objects.filter(q_filter).annotate(contributor=F('user_id__username'))

    for log in latest_file_logs:
        for file in files:
            if file['id'] == log.file_id:
                file['version'] = log.version
                file['contributor'] = log.contributor
                break

    return Response(files, status=status.HTTP_200_OK)


def download_file(request, file_id):
    user = request.user
    error_msg = {}

    error_code = is_valid_access(user.id, file_id, error_msg)
    if error_code:
        return Response(error_msg, error_code)

    response = download_file_from(FILESERVER_URL, user.id, file_id)

    if response.status_code != 200:
        return Response(response.content, status=response.status_code)

    response.headers['version'] = Log.objects \
        .filter(file_id=file_id) \
        .aggregate(version=Max('version'))['version']

    httpResponse = HttpResponse(
        content=response.content,
        status=response.status_code
    )

    for header, value in response.headers.items():
        httpResponse[header] = value

    return httpResponse


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def files_detail(request):
    if request.method == 'GET':
        return list_files(request)
    elif request.method == 'POST':
        return upload_file(request)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def file_detail(request, file_id):
    if request.method == 'GET':
        return download_file(request, file_id)
    elif request.method == 'PUT':
        return update_file(request, file_id)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_file(request, file_id):
    file_response = download_file(request, file_id)

    if file_response.status_code != 200:
        return Response(file_response.content, status=file_response.status_code)

    data_response = get_file_data_from(FILESERVER_URL, file_id)

    if data_response.status_code != 200:
        return Response(data_response.content, status=data_response.status_code)

    log = Log.objects.filter(file_id=file_id).latest('timestamp')
    data = {'contributors': data_response.json()['keys'], 'signature': log.signature}

    try:
        is_valid_signature(file_response.content, data, log.user_id, log.version)
    except ValidationError:
        recovery = recover_data_from(FILESERVER_URL, 2)

        if recovery.status_code != 200:
            return Response(recovery.content, status=recovery.status_code)

        last_backup_date = Backup.objects.latest('timestamp').timestamp
        Log.objects.filter(timestamp__gt=last_backup_date).delete()

        return Response(status=status.HTTP_202_ACCEPTED)

    return Response({'file_id': [f"No integrity problems detected."]}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def backup_data(request):
    backup_timestamp = datetime.now()

    query_set = Log.objects.values('file_id').annotate(max_timestamp=Max('timestamp')).order_by('file_id')
    query_filter = Q()

    for entry in query_set:
        query_filter |= (Q(file_id=entry['file_id']) & Q(timestamp=entry['max_timestamp']))

    latest_logs = Log.objects.filter(query_filter)
    serial = DataSerializer(latest_logs, many=True)

    for entry in serial.data:
        entry['contributors'] = list(Log.objects
                                     .filter(file_id=entry['file_id'], version=0)
                                     .values_list('user_id', flat=True)
                                     .order_by('user_id'))

    data_responses = backup_data_to([BACKUPSERVER1_URL, BACKUPSERVER2_URL],
                                    serial.data)  # Colocar na lista bakup server 2 tb

    system_status = []
    for response in data_responses:
        if response.status_code != 200:
            return Response(response.content, status=response.status_code)

        system_status.append(response.json()['system_status'])

    if sum(system_status) == len(data_responses):  # everything OK

        backup_serial = BackupSerializer(data={
            'timestamp': backup_timestamp,
            'successful': True})

        backup_serial.is_valid(raise_exception=True)
        backup_serial.save()

        return Response(status=status.HTTP_202_ACCEPTED)
    elif sum(system_status) == 0:  # file Server corruption
        recovery = recover_data_from(FILESERVER_URL, 2)

        if recovery.status_code != 200:
            return Response(recovery.content, status=recovery.status_code)

        last_backup_date = Backup.objects.latest('timestamp').timestamp
        Log.objects.filter(timestamp__gt=last_backup_date).delete()

        return Response(status=status.HTTP_205_RESET_CONTENT)
    else:  # one backup server corrupt
        backup_serial = BackupSerializer(data={
            'timestamp': backup_timestamp,
            'successful': True})

        backup_serial.is_valid(raise_exception=True)
        backup_serial.save()

        # Ignore wrong BU Server?
        # Place BU server in black list until a physical fix is done?
        # Logs Server is not able to force BU Server to backup from FS

    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
