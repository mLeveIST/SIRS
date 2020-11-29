from pathlib import Path

from django.core import management

def backup_cmd(cmd, op=None):
	if op:
		management.call_command(cmd, op, verbosity=0, interactive=False)
	else:
		management.call_command(cmd, verbosity=0, interactive=False)

# TODO week of RIR development
def check_integrity(logs_db, files_db):
	return 1

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

def empty_temp_files():
	return Path('temp/filestemp.tar').stat().st_size == 0 \
		or Path('temp/dbtemp.dump').stat().st_size == 0