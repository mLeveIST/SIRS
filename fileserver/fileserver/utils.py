import base64
from pathlib import Path
from django.core import management


def bytes_to_string(ebytes: bytes) -> str:
    return base64.b64encode(ebytes).decode()


def string_to_bytes(text: str) -> bytes:
    return base64.b64decode(text.encode())


def backup_cmd(cmd, op=None):
    if op:
        management.call_command(cmd, op, verbosity=0, interactive=False)
    else:
        management.call_command(cmd, verbosity=0, interactive=False)


# TODO check exceptions
def remove_files(path, depth=0):
    root = Path(path)
    for node in root.glob('*'):
        if node.is_file():
            node.unlink()
        else:
            remove_files(node, depth=depth+1)
    if depth:
        root.rmdir()


def empty_directory(path):
    return not Path(path).exists()
