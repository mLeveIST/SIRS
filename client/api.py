import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from requests.api import head
from utils import validate_response, bytes_to_string, string_to_bytes

SERVER_IP = "localhost:8000"
session_token = ""


def api_url(route: str): return f"http://{SERVER_IP}/api/{route}"


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
    login_data = {
        "username": username,
        "password": password
    }

    response = requests.post(api_url("users/login/"), data=login_data)
    validate_response(response, raise_exception=True)
    return response.json()


def list_files(token: str) -> dict:
    headers = {'Authorization': f'Token {token}'}
    response = requests.get(api_url("files/"), headers=headers)
    validate_response(response, raise_exception=True)
    return response.json()


def upload_file(token: str, efile: bytes, sign: bytes, ekeys: list[bytes], contributors: list[str]) -> dict:
    headers = {'Authorization': f'Token {token}'}
    files_data = {'file': efile}

    keys_data = [{'username': contributors[i], 'key': bytes_to_string(ekeys[i])} for i in range(len(contributors))]
    data = {'keys': keys_data, 'sign': bytes_to_string(sign)}

    response = requests.post(api_url("files/"), headers=headers, files=files_data, data=data)
    validate_response(response, raise_exception=True)
    return response.json()


def update_file(token: str, file_id: int, efile: bytes, ekey: bytes, version: int, sign: bytes) -> dict:
    headers = {'Authorization': f'Token {token}'}
    files_data = {'file': efile}
    data = {'key': bytes_to_string(ekey), 'version': version, 'sign': bytes_to_string(sign)}

    response = requests.put(api_url(f"files/{file_id}/"), headers=headers, files=files_data, data=data)
    validate_response(response, raise_exception=True)
    return response.json()


def download_file(token: str, file_id: int) -> dict:
    headers = {'Authorization': f'Token {token}'}
    response = requests.get(api_url(f"files/{file_id}/"), headers=headers)
    validate_response(response, raise_exception=True)
    return {'file': response.content, 'key': string_to_bytes(response.headers['key'])}


def user_pubkey(username: str) -> dict:
    response = requests.get(api_url(f'users/{username}/pubkey/'))
    validate_response(response)
    return response.json()


def file_contributors(token: str, file_id: int) -> dict:
    headers = {'Authorization': f'Token {token}'}
    response = requests.get(api_url(f'files/{file_id}/users/'), headers=headers)
    validate_response(response)
    return response.json()
