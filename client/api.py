import requests
from cryptography.hazmat.primitives import serialization

log_server_ip = "http://localhost:8000"
session_token = ""


def is_response_status_ok(response) -> bool:
    return 200 <= response.status_code < 300


def error_message(request, code, message):
    return "Error in {} API request. Code: {}\nError message: {}".format(request, code, message)


def register(username: str, password: str, pubkey) -> bool:
    pubkey_serialized = pubkey.public_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.PKCS1)
    register_data = {
        "username": username,
        "password": password,
        "pubkey": pubkey_serialized
    }

    response = requests.post("{}/api/user/register/".format(log_server_ip), data=register_data)

    if not is_response_status_ok(response):
        raise RuntimeError(error_message('register', response.status_code, response.content))

    return response.json()


def login(username: str, password: str) -> bool:
    login_data = {
        "username": username,
        "password": password
    }

    response = requests.post("{}/api/user/login/".format(log_server_ip), data=login_data)

    if not is_response_status_ok(response):
        raise RuntimeError(error_message('login', response.status_code, response.content))

    return response.json()


def create_file(filepath: str, keys: list, contributors=None) -> bool:
    """
    - Get file from file path
    - Encrypt it with PGP
    - Create digest of encrypted file, user keys, list of contributors
    - Sign digest
    - Create HTTP request with encrypted file, list of user keys encrypted, list of contributors
    - Save file_id
    """
    if contributors is None:
        contributors = []
    pass


def update_file(file_id: int, keys: list) -> bool:
    """
    - Get file from file path
    - Encrypt it with PGP
    - Create digest of encrypted file, user keys, list of contributors
    - Sign digest
    - Create HTTP request with encrypted file, list of user keys encrypted, list of contributors
    """
    pass


def get_file(file_id: int) -> bool:
    """
    - Create HTTP request with file_id
    - Decrypt file with PGP
    - Save file
    """
    pass


def get_user_certificates(usernames: list) -> list:
    pass
