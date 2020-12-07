from django.core import management

from pathlib import Path

import base64


def backup_cmd(cmd, op=None):
    if op:
        management.call_command(cmd, op, verbosity=0, interactive=False)
    else:
        management.call_command(cmd, verbosity=0, interactive=False)


# TODO check exceptions
def remove_files(path, depth=0, remove_self=False):
    root = Path(path)

    try:
        for node in root.glob('*'):
            if node.is_file():
                print("HERE3")
                node.unlink()
            else:
                remove_files(node, depth=depth+1)
        if depth or remove_self:
            root.rmdir()
    except FileNotFoundError:
        pass # Raise Integrity Error to Logs Server maybe


def empty_directory(path):
    return not Path(path).exists()


def bytes_to_string(ebytes: bytes) -> str:
    return base64.b64encode(ebytes).decode()


def string_to_bytes(text: str) -> bytes:
    return base64.b64decode(text.encode())


