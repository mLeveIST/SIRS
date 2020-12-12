from cryptography.exceptions import InvalidSignature

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed

from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers.algorithms import AES

from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from backupserver import utils

from typing import List


def check_integrity(files_db: list, logs_db: list) -> int:
	if len(files_db) == 0 or len(logs_db) == 0:
		return 0

	if len(files_db) != len(logs_db):
		return 0

	for file, log in zip(files_db, logs_db):
		if not check_db_relations(file, log):
			return 0

		if not check_digest(file, log):
			return 0

	return 1


def check_db_relations(file: dict, log: dict) -> bool:
	if file["id"] != log["file_id"]:
		return False

	if len(file["keys"]) != len(log["contributors"]):
		return False

	for key, contributor in zip(file["keys"], log["contributors"]):
		if key["file_id"] != log["file_id"]:
			return False

		if key["user_id"] != contributor:
			return False

	return True


def check_digest(file: dict, log: dict) -> bool:
	version = log['version']
	location = f"/var/repo/backupserver/files{file['file']}" #For prod
	#location = f"files/{file['file']}" # For dev
	with open(location, 'rb') as fd:
		edata = fd.read()

	ekeys = [utils.string_to_bytes(key['key'])[:-12] for key in file['keys']]
	eversion = version.to_bytes((version.bit_length() + 7) // 8, 'big')

	public_key = load_pem_public_key(log['pubkey'].encode())
	
	if not isinstance(public_key, rsa.RSAPublicKey):
		print("Error loading public key!")
		return False

	try:
		public_key.verify(
			utils.string_to_bytes(log['signature']),
			utils.hash_data([edata] + ekeys + [eversion]),
			padding.PSS(
				mgf=padding.MGF1(hashes.SHA256()),
				salt_length=padding.PSS.MAX_LENGTH
			),
			Prehashed(hashes.SHA256())
		)
	except InvalidSignature:
		print("Digest is not valid! Integrity error!")
		return False

	return True
