from cryptography.hazmat.primitives import hashes
from typing import List

import base64


def bytes_to_string(ebytes: bytes) -> str:
    return base64.b64encode(ebytes).decode()


def string_to_bytes(text: str) -> bytes:
    return base64.b64decode(text.encode())


def hash_data(data: List[bytes]) -> bytes:
    hashfunc = hashes.Hash(hashes.SHA256())
    for chunk in data:
        hashfunc.update(chunk)
    return hashfunc.finalize()