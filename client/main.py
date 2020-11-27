from sys import argv
from pgp import encrypt_PGP_AES_GCM

def main(args: list):
	data = b'Faz o PHP Manel!'
	version = b'1'

	to_send = encrypt_PGP_AES_GCM(data, version)
	print(to_send)


if __name__ == "__main__":
	main(argv)