import base64


def bytes_to_string(ebytes: bytes) -> str:
    return base64.b64encode(ebytes).decode()


def string_to_bytes(text: str) -> bytes:
    return base64.b64decode(text.encode())
