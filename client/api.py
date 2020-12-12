import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from utils import validate_response, bytes_to_string, string_to_bytes, json_payload

requests.packages.urllib3.disable_warnings()
SERVER_IP = "log"  # for prod
#SERVER_IP = "localhost:8000"  # for dev
session_token = ""


def api_url(route: str): return f"https://{SERVER_IP}/api/{route}"


def register(username: str, password: str, pubkey: RSAPublicKey) -> dict:
    pubkey_serialized = pubkey.public_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.PKCS1)
    register_data = {
        "username": username,
        "password": password,
        "pubkey": pubkey_serialized
    }

    response = requests.post(api_url("users/register/"), data=register_data)
    validate_response(response, raise_exception=True)

    return response.json()


def login(username: str, password: str) -> dict:
    login_data = {"username": username, "password": password}

    response = requests.post(api_url("users/login/"), data=login_data)
    validate_response(response, raise_exception=True)

    return response.json()


def list_files(token: str) -> dict:
    headers = {'Authorization': f'Token {token}'}
    response = requests.get(api_url("files/"), headers=headers)
    validate_response(response, raise_exception=True)
    return response.json()


def upload_file(token: str, efile: bytes, sign: bytes, ekeys: 'list[bytes]', contributors: 'list[str]') -> dict:
    headers = {'Authorization': f'Token {token}'}
    files_data = {'file': efile}
    contrib_data = [{'username': contributors[i], 'key': bytes_to_string(ekeys[i])} for i in range(len(contributors))]
    data = {'contributors': contrib_data, 'signature': bytes_to_string(sign)}

    response = requests.post(api_url("files/"), headers=headers, files=files_data, data=json_payload(data))
    validate_response(response, raise_exception=True)

    return response.json()


def update_file(token: str, file_id: int, efile: bytes, sign: bytes, version: int, ekeys: 'list[bytes]', contributors: 'list[str]') -> dict:
    headers = {'Authorization': f'Token {token}'}
    files_data = {'file': efile}
    contrib_data = [{'username': contributors[i], 'key': bytes_to_string(ekeys[i])} for i in range(len(contributors))]
    data = {'contributors': contrib_data, 'version': version, 'signature': bytes_to_string(sign)}

    response = requests.put(api_url(f"files/{file_id}/"), headers=headers, files=files_data, data=json_payload(data))
    validate_response(response, raise_exception=True)

    return {}


def download_file(token: str, file_id: int) -> dict:
    headers = {'Authorization': f'Token {token}'}

    response = requests.get(api_url(f"files/{file_id}/"), headers=headers)
    validate_response(response, raise_exception=True)

    return {'file': response.content, 'key': string_to_bytes(response.headers['key'])}


def user_pubkey(token: str, username: str) -> dict:
    headers = {'Authorization': f'Token {token}'}

    response = requests.get(api_url(f'users/{username}/'), headers=headers)
    validate_response(response)

    pubkey = serialization.load_pem_public_key(response.json()['pubkey'].encode())
    return {'pubkey': pubkey}


def file_contributors(token: str, file_id: int) -> dict:
    headers = {'Authorization': f'Token {token}'}

    response = requests.get(api_url(f'files/{file_id}/users/'), headers=headers)
    validate_response(response)

    contributors = response.json()
    for contributor in contributors:
        contributor['pubkey'] = serialization.load_pem_public_key(contributor['pubkey'].encode())

    return contributors


def report_file(token: str, file_id: int) -> dict:
    headers = {'Authorization': f'Token {token}'}

    response = requests.get(api_url(f'files/{file_id}/report/'), headers=headers)
    validate_response(response)  # raise_exception=False -> handle exception, what to do?

    return {'status': response.status_code}


def backup_files(token: str):
    headers = {'Authorization': f'Token {token}'}

    response = requests.get(api_url('files/backup/'), headers=headers)
    validate_response(response)
    input(response.status_code)
    return {}
