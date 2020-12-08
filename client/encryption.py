from cryptography.exceptions import InvalidTag

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.primitives.ciphers.algorithms import AES

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.asymmetric import padding, rsa, utils
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
import hashlib

from sys import stderr
import os

MAX_DATA_SIZE = 4294967296  # 4GB (TEMP)
RAND_KEY_SIZE = 256  # bits
BLOCK_SIZE = 128  # bits


def generate_RSA_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return {'private': private_key, 'public': public_key}


def encrypt_file(data: bytes, version: int, private_key: RSAPrivateKey, public_keys: 'list[RSAPublicKey]') -> dict:
    aes_key = AESGCM.generate_key(bit_length=256)  # also uses urandom()
    cipher = AESGCM(aes_key)
    nonce = os.urandom(12)  # 96 bits is optimal

    # Encrypt file data
    try:
        edata = cipher.encrypt(nonce, data, None)
    except OverflowError:  # if data is > 2^32 bytes
        raise Exception("Data is too big (exceeds 4GB)!")

    # Encrypt AES key with contributers public keys
    ekeys = []
    for pub_key in public_keys:
        ekeys.append(pub_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),  # Mask Generation Function
                algorithm=hashes.SHA256(),
                label=None
            )
        ))

    # Hash edata, ekeys, and file version
    hashfunc = hashes.Hash(hashes.SHA256())
    hashfunc.update(edata)
    for ekey in ekeys:
        hashfunc.update(ekey)
    hashfunc.update(str(version).encode())
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

    return {'efile': edata, 'ekeys': [ekey + nonce for ekey in ekeys], 'version': version, 'sign': signature}


def decrypt_file(edata: bytes, ekey: bytes, private_key: RSAPrivateKey):
    # Decrypt random key and get nonce
    nonce = ekey[-12:]
    aes_key = private_key.decrypt(
        ekey[:-12],
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    cipher = AESGCM(aes_key)

    # Decrypt file data
    try:
        data = cipher.decrypt(nonce, edata, None)
    except InvalidTag:
        raise Exception("Integrity attack!")  # If edata, nonce or aes key were changed

    return data
