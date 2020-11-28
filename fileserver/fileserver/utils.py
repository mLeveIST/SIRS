from pathlib import Path

from django.core import management

def backup_cmd(cmd):
	management.call_command(cmd, verbosity=0, interactive=False)

# TODO check exceptions
def remove_files(path):
	file_list = list(Path(path).glob('*'))
	for file in file_list:
		file.unlink()

def empty_temp_files():
	return Path('temp/filestemp.tar').stat().st_size == 0 \
		or Path('temp/dbtemp.dump').stat().st_size == 0