import requests
from cryptography.hazmat.primitives import serialization
from utils import validate_response, bytes_to_string, string_to_bytes

SERVER_IP = "localhost:8000"
session_token = ""


def api_url(route): return "http://{}/api/{}".format(SERVER_IP, route)


def register(username: str, password: str, pubkey) -> dict:
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


def list_files(token: str):
    headers = {'Authorization': 'Token {}'.format(token)}
    response = requests.get(api_url("files/"), headers=headers)
    validate_response(response, raise_exception=True)
    return response.json()


def upload_file(token: str, efile: bytes, ekey: bytes, sign: bytes) -> dict:
    headers = {'Authorization': 'Token {}'.format(token)}
    files_data = {'file': efile}
    data = {'key': bytes_to_string(ekey), 'sign': bytes_to_string(sign)}

    response = requests.post(api_url("files/"), headers=headers, files=files_data, data=data)
    validate_response(response, raise_exception=True)
    return


def update_file(token: str, file_id: int, efile: bytes, ekey: bytes, version: int, sign: bytes) -> bool:
    headers = {'Authorization': 'Token {}'.format(token)}
    files_data = {'file': efile}
    data = {'key': bytes_to_string(ekey), 'version': version, 'sign': bytes_to_string(sign)}

    response = requests.put(api_url("files/{}/".format(file_id)), headers=headers, files=files_data, data=data)


def download_file(token, file_id):
    headers = {'Authorization': 'Token {}'.format(token)}
    response = requests.get(api_url("files/{}/".format(file_id)), headers=headers)
    validate_response(response, raise_exception=True)
    return {'efile': response.content, 'ekey': string_to_bytes(response.headers['key'])}


def get_user_certificates(usernames: list) -> list:
    pass
