import requests


def register(username: str, password: str) -> bool:
    """
    - Create HTTP request with username and password
    """
    pass


def login(username: str, password: str) -> bool:
    """
    - Create HTTP request with username and password
    - Save token (session) login
    """
    pass


def create_file(filepath: str, keys: list, contributors=[]) -> bool:
    """
    - Get file from file path
    - Encrypt it with PGP
    - Create digest of encrypted file, user keys, list of contributors
    - Sign digest
    - Create HTTP request with encrypted file, list of user keys encrypted, list of contributors
    - Save file_id
    """
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
