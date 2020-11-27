from sys import argv
from pgp import encrypt_PGP_AES_GCM, encrypt_PGP_AES_CBC, decrypt_PGP_AES_CBC

def main(args: list):
	data = b'Faz o PHP Manel!'
	version = b'1'

	to_send = encrypt_PGP_AES_CBC(data, version)
	print(f"\nClient PGP Encryption:\n- edata: {to_send[0]}\n- ekey: {to_send[1]}")
	print(f"- version: {to_send[2]}\n- signature: {to_send[3]}")

	received_data = decrypt_PGP_AES_CBC(to_send[0], to_send[1])
	print(f"\nClient PGP Decryption:\n- {received_data}\n")


if __name__ == "__main__":
	main(argv)