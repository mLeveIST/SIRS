from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed

from rest_framework import status
from rest_framework.serializers import ValidationError

from api.models import User, Log
from logserver import utils


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

    is_valid_signature(request.FILES['file'].read(), data, user, 1)


def is_valid_update_file_request(request, data: dict, file_id: int, users: list):

    error_msg = {}
    user = request.user
    contributors = list(Log.objects.filter(file_id=file_id, version=0).values_list('user_id', flat=True))

    error_code = is_valid_access(user.id, file_id, error_msg, contributors)
    if error_code:
        error = ValidationError(error_msg)
        error.status_code = error_code
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

    is_valid_signature(request.FILES['file'].read(), data, user, data['version'])


def is_valid_access(user_id: int, file_id: int, msg: dict, contributors=None) -> int:

    if not contributors:
        contributors = list(Log.objects \
            .filter(file_id=file_id, version=0) \
            .values_list('user_id', flat=True))

        if not contributors:
            msg['file_id'] = [f"File with id '{file_id}' does not exist."]
            return status.HTTP_404_NOT_FOUND

    if user_id not in contributors:
        msg['response'] = [f"Permission Denied"]
        return status.HTTP_403_FORBIDDEN

    return 0


def is_valid_signature(edata: bytes, data: dict, user, version: int):
    try:
        ekeys = [is_valid_encoding(contributor['key'], 'key')[:-12] for contributor in data['contributors']]
        eversion = version.to_bytes((version.bit_length() + 7) // 8, 'big')
        signature = is_valid_encoding(data['signature'], 'signature')

        public_key = serialization.load_der_public_key(user.pubkey)

        public_key.verify(
            signature,
            utils.hash_data([edata] + ekeys + [eversion]),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            Prehashed(hashes.SHA256())
        )
    except InvalidSignature:
        raise ValidationError({'signature': [f"Integrity verification failed."]})


def is_valid_encoding(text: str, tag: str) -> bytes:
    try:
        return utils.string_to_bytes(text)
    except Exception:
        raise ValidationError({f'{tag}': [f"Must be a base64 encoded string."]})

