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
	print(files_db)
	print(logs_db)
	
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

	with open(f"files/{file['file']}", 'rb') as fd:
		edata = fd.read()

	ekeys = [utils.string_to_bytes(key['key'])[:-12] for key in file['keys']]
	eversion = version.to_bytes((version.bit_length() + 7) // 8, 'big')

	public_key = load_pem_public_key(utils.string_to_bytes(log['pubkey']))
	
	if not isinstance(public_key, rsa.RSAPublicKey):
		print("Error loading public key!")
		return 0

	try:
		public_key.verify(
			log['signature'],
			utils.hash_data([edata] + ekeys + [eversion]),
			padding.PSS(
				mgf=padding.MGF1(hashes.SHA256()),
				salt_length=padding.PSS.MAX_LENGTH
			),
			Prehashed(hashes.SHA256())
		)
	except InvalidSignature:
		print("Digest is not valid! Integrity error!")
		return 0

	return 1



"""

EXAMPLE JSON FORMAT

"""

"""
LOGS DATA
[
  {
    "file_id": 1,
    "user_id": 1,
    "signature": "cbati37uya389go2hp2q4uiowefubj",
    "pub_key": "cfjvghkbn",
    "version": 12,
    "contributors": [1, 2]
  },
  {
    "file_id": 2,
    "user_id": 1,
    "signature": "treytyjkuvhbjnuyrt567ioj2efnfh",
    "pub_key": "c7r56vt8yiu",
    "version": 1,
    "contributors": [1]
  },
  {
    "..."
  }
]
"""

"""
FILES DATA
[
  {
    "id": 1,
    "file": "/file/path/filename.file",
    "keys": [
      {
        "user_id": 1,
        "file_id": 1,
        "key": "bckyatr3q378qv3i7vq3ciq3vq78"
      },
      {
        "user_id": 2,
        "file_id": 1,
        "key": "lbc7q6giqpvygcbh48fuifywfb2u"
      }
    ]
  },
  {
    "id": 2,
    "efile": "/file/path/filename.file",
    "keys": [
      {
        "user_id": 1,
        "file_id": 2,
        "key": "h7hng53nviox9083785bud"
      }
    ]
  }
  {
    "..."
  }
]
"""







