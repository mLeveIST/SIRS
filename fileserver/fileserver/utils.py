from pathlib import Path

from django.core import management

def backup_cmd(cmd, op):
	management.call_command(cmd, op, verbosity=0, interactive=False)

# TODO check exceptions
def remove_files(path):
	file_list = list(Path(path).glob('*'))
	for file in file_list:
		file.unlink()