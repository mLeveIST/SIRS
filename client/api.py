import requests

log_server_ip = "http://192.168.57.10"
session_token = ""
pubkey = "something"  # Go get from file


def is_response_status_ok(response) -> bool:
    return 200 < response.status_code < 300


def register(username: str, password: str) -> bool:
    """
    - Get pub key
    - Create HTTP request with username and password
    """
    register_data = {
        "username": username,
        "password": password,
        "pubkey": pubkey
    }

    response = requests.post("{}/api/user/register/".format(log_server_ip),
                             data=register_data
                             )

    if is_response_status_ok(response):
        global session_token
        session_token = response.json()["token"]
        return True

    print("Http response not ok: {}".format(response.json()))
    return False


def login(username: str, password: str) -> bool:
    """
    - Create HTTP request with username and password
    - Save token (session) login
    """
    login_data = {
        "username": username,
        "password": password
    }

    response = requests.post("{}/api/user/register/".format(log_server_ip),
                             data=login_data
                             )

    if is_response_status_ok(response):
        global session_token
        session_token = response.json()["token"]
        return True

    print("Http response not ok: {}".format(response.json()))
    return False


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
