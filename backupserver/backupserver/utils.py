from django.core import management
from pathlib import Path

import os

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





















