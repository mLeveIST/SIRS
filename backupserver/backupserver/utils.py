from pathlib import Path

from django.core import management

def backup_cmd(cmd, op):
	management.call_command(cmd, op, verbosity=0, interactive=False)

# TODO week of RIR development
def check_integrity(logs_db, files_db):
	return 1

# TODO check exceptions
def remove_files(path):
	file_list = list(Path(path).glob('*'))
	for file in file_list:
		file.unlink()

def empty_temp_files():
	return Path('temp/filestemp.tar').stat().st_size == 0 \
		or Path('temp/dbtemp.dump').stat().st_size == 0