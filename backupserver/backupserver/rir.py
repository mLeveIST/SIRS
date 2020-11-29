from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.primitives.ciphers.algorithms import AES

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.asymmetric import padding, rsa, utils

from typing import List
from sys import stderr

import hashlib
import os

"""
1. Number of log objects must equal number of file objects
2. file IDs must be equal for each log and file object
3. Number of keys for each file must equal number of contributors
4. File Id associated with each key must equal file ID that has the key
5. Each key user ID must be in contributors

6. Digest must equal to calculated digest
"""
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
	if file["id"] != log["id"]:
		return False

	if len(file["ekeys"]) != len(log["contributors"]):
		return False

	for key, contributor in zip(file["ekeys"], log["contributors"]):
		if key["file_id"] != log["id"]:
			return False

		if key["user_id"] != contributor:
			return False

	return True


def check_digest(file: dict, log: dict) -> bool:
	file_path = f'files/{file["efile"]}'
	ekeys = [ekey["evalue"].encode()[:-12] for ekey in file["ekeys"]]

	digest = create_digest(file_path, ekeys, log["version"])

	return digest != log["digest"].encode()


def create_digest(file_path: str, ekeys: List[bytes], version: int) -> bytes:
	with open(file_path) as file:
		edata = file.read().encode()

	# Hash edata, ekeys, and file version
	hashfunc = hashes.Hash(hashes.SHA256())
	hashfunc.update(edata)
	for ekey in ekeys:
		hashfunc.update(ekey)
	hashfunc.update(version)

	return hashfunc.finalize()




"""

EXAMPLE JSON FORMAT

"""

"""
LOGS DATA
[
  {
    "file_id": 1,
    "user_id": 1,
    "digest": "cbati37uya389go2hp2q4uiowefubj",
    "version": 12,
    "contributors": [1, 2]
  },
  {
    "file_id": 2,
    "user_id": 1,
    "digest": "treytyjkuvhbjnuyrt567ioj2efnfh",
    "version": 1,
    "contributors": [1]
  },
  {
    "....."
  }
]
"""

"""
FILES DATA
[
  {
    "id": 1,
    "efile": "/file/path/filename.file",
    "ekeys": [
      {
        "user_id": 1,
        "file_id": 1,
        "evalue": "bckyatr3q378qv3i7vq3ciq3vq78"
      },
      {
        "user_id": 2,
        "file_id": 1,
        "evalue": "lbc7q6giqpvygcbh48fuifywfb2u"
      }
    ]
  },
  {
    "id": 2,
    "efile": "/file/path/filename.file",
    "ekeys": [
      {
        "user_id": 1,
        "file_id": 2,
        "evalue": "h7hng53nviox9083785bud"
      }
    ]
  }
  {
    "....."
  }
]
"""















