from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils

from rest_framework import status
from rest_framework.serializers import ValidationError

from api.models import User, Log

import base64
from typing import List

def string_to_bytes(text: str, tag: str) -> bytes:
    try:
        return base64.b64decode(text.encode())
    except Exception:
        raise ValidationError({f'{tag}': [f"Must be a base64 encoded string."]})


def is_valid_upload_file_request(request, data: dict, users: list):

    user = request.user

    if user.username != data['contributors'][0]['username']:
        raise ValidationError({'contributors': [f"User '{user.username}' missing."]})

    for contributor in data['contributors']:
        try:
            u = User.objects.get(username=contributor['username'])
        except User.DoesNotExist:
            raise ValidationError({'contributors': [f"User '{contributor['username']}' does not exist."]})

        if u in users:
            raise ValidationError({'contributors': [f"User '{contributor['username']}' repeated."]})

        users.append(u)

    try:
        check_signature(request.FILES['file'].read(), data, user, 1)
    except InvalidSignature:
        raise ValidationError({'signature': [f"Integrity verification failed."]})


def is_valid_update_file_request(request, data: dict, file_id: int, users: list):

    user = request.user
    contributors = list(Log.objects.filter(file_id=file_id, version=0).values_list('user_id', flat=True))

    if not contributors:
        raise ValidationError({'file_id': [f"File with id '{file_id}' does not exist."]})

    if user.id not in contributors:
        error = ValidationError({'response': [f"Permission Denied"]})
        error.status_code = status.HTTP_403_FORBIDDEN
        raise error

    if user.username != data['contributors'][0]['username']:
        raise ValidationError({'contributors': [f"User '{user.username}' missing."]})

    for contributor in data['contributors']:
        try:
            u = User.objects.get(username=contributor['username'])
        except User.DoesNotExist:
            raise ValidationError({'contributors': [f"User '{contributor['username']}' does not exist."]})

        if u in users:
            raise ValidationError({'contributors': [f"User '{contributor['username']}' repeated."]})

        if u.id not in contributors:
            raise ValidationError({'contributors': [f"User '{contributor['username']}' is not a contributor for the file."]})

        users.append(u)
        contributors.remove(u.id)

    if contributors:
        raise ValidationError({'contributors': [f"Missing some contributors."]})

    log = Log.objects.filter(file_id=file_id).latest('timestamp')

    if data['version'] != log.version + 1:
        raise ValidationError({'version': [f"Wrong version. Got '{data['version']}', expected '{log.version + 1}'."]})

    try:
        check_signature(request.FILES['file'].read(), data, user, data['version'])
    except InvalidSignature:
        raise ValidationError({'signature': [f"Integrity verification failed."]})


def check_signature(edata: bytes, data: dict, user, version: int):

    ekeys = [string_to_bytes(contributor['key'], 'key')[:-12] for contributor in data['contributors']]
    eversion = version.to_bytes((version.bit_length() + 7) // 8, 'big')
    signature = string_to_bytes(data['signature'], 'signature')

    public_key = serialization.load_der_public_key(user.pub_key)

    public_key.verify(
        signature,
        create_digest(edata, ekeys, eversion),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        utils.Prehashed(hashes.SHA256())
    )


def create_digest(edata: bytes, ekeys: List[bytes], eversion: bytes) -> bytes:
    hashfunc = hashes.Hash(hashes.SHA256())
    hashfunc.update(edata)
    for ekey in ekeys:
        hashfunc.update(ekey)
    hashfunc.update(eversion)

    return hashfunc.finalize()
