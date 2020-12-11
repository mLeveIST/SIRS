import os
import json
import base64
from typing import Callable

from requests.models import Response


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


def clear_before(func: Callable):
    clear_screen()
    func()


def json_payload(data: dict) -> dict:
    return {'json': json.dumps(data)}


def bold(text: str) -> str:
    return "\033[1m" + text + "\033[0m"


def validate_response(response, raise_exception=True) -> bool:
    if not (200 <= response.status_code < 300):
        if raise_exception:
            try:
                response.json()  # if error data is html will raise exception
                raise ServerException(response)
            except ValueError:
                content = response.content
                raise ConnectionError("Error when making a {} request to {}. Returned {} {} with: {}".format(
                    response.request.method, response.request.url, response.status_code, response.reason, content))
        return False
    return True


def is_client_error(status_code): return 400 <= status_code < 500


class ServerException(Exception):
    def __init__(self, response: Response, message: str = 'default'):
        self.response = response
        self.status = response.status_code
        self.reason = response.reason

        self.request = response.request
        self.method = response.request.method
        self.url = response.request.url

        self.data = response.json()
        self.message = message if message != 'default' else f'Error {self.status} {self.reason} : {self.url}'

        values = list(self.data.values())
        self.error_message = values[0] if isinstance(values[0], str) else values[0][0]

        super().__init__(self.message)
