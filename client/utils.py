import os
import json
import base64


def bytes_to_string(ebytes: bytes) -> str:
    return base64.b64encode(ebytes).decode()


def string_to_bytes(text: str) -> bytes:
    return base64.b64decode(text.encode())


def clear_screen():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')


def validate_response(response, raise_exception=True) -> bool:
    if not (200 <= response.status_code < 300):
        if raise_exception:
            try:
                content = response.json()
            except:
                content = response.content
            raise ConnectionError("Error when making a {} request to {}. Returned {} {} with: {}".format(
                response.request.method, response.request.url, response.status_code, response.reason, content))
        return False
    return True


def json_payload(data: dict) -> dict:
    return {'json': json.dumps(data)}
