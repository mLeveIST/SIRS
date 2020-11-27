from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.primitives.ciphers.algorithms import AES

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, utils
import hashlib

from sys import stderr
import os


# Also provides authenticaton by itself, but we will still need to hash to authenticate key and version together
# Redundancy is good ?
def encrypt_PGP_AES_GCM(data: bytes, version: bytes) -> tuple:

	random_key = AESGCM.generate_key(bit_length=256) # also uses urandom()
	cipher = AESGCM(random_key)
	nonce = os.urandom(12) # 96 bits is optimal

	# Encrypt file data
	try:
		edata = cipher.encrypt(nonce, data, None)
	except OverflowError: # if data is > 2^32 bytes
		error(f"Data is too big (exceeds 4GB)!")

	# TODO - Get Private Key
	#
	# with open("path/to/key.pem", "rb") as key_file: # needs to be .pem ?
	# 	private_key = serialization.load_pem_private_key(
	# 		key_file.read(),
	# 		password=None, # Add password ?
	# 	)
	#
	# public_key = private_key.public_key() # Also read from file ?

	# TEMP
	private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
	public_key = private_key.public_key()

	# Encrypt random key
	ekey = public_key.encrypt(
		random_key,
		padding.OAEP(
			mgf=padding.MGF1(algorithm=hashes.SHA256()), # Mask Generation Function
			algorithm=hashes.SHA256(),
			label=None
		)
	)

	# Hash edata, ekey, and file version
	hashfunc = hashes.Hash(hashes.SHA256())
	hashfunc.update(edata)
	hashfunc.update(ekey)
	hashfunc.update(version)
	digest = hashfunc.finalize()

	# Sign digest
	signature = private_key.sign(
		digest,
		padding.PSS(
			mgf=padding.MGF1(hashes.SHA256()),
			salt_length=padding.PSS.MAX_LENGTH
		),
		utils.Prehashed(hashes.SHA256())
	)

	return (edata, ekey, version, signature)



def decrypt_PGP_AES_GCM(edata: bytes, ekey: bytes):
	pass # TODO


# Does not provide authentication
# Needs padding, so is suceptible to padding oracle attacks
def encrypt_PGP_AES_CBC(data: bytes):
	random_key = os.urandom(32)
	iv = os.urandom(16)
	cipher = Cipher(AES(random_key), modes.CBC(iv))

	# ...