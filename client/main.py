#!/usr/bin/env python3

from sys import argv
from encryption import generate_RSA_keys, encrypt_file, decrypt_file
from cryptography.hazmat.primitives import serialization
from selectmenu import SelectMenu
import os
import api
from getpass import getpass

token = None
key_pair = None


def action_login():
    global token, key_pair
    key_pair = load_keys()

    user = input("Username: ")
    pw = getpass("Password: ")
    clear_screen()

    token = api.login(user, pw)["token"]
    return mainMenu.select_action()


def action_register(key_method):
    global token, key_pair
    if key_method == 'generate':
        key_pair = generate_RSA_keys()
    elif key_method == 'load':
        key_pair = load_keys()
    else:
        raise SystemError("Something went wrong when choosing the key method")

    user = input("Username: ")
    pw = getpass("Password: ")
    if pw != getpass("Confirm Password: "):
        raise ValueError("Passwords don't have the same value")
    clear_screen()

    token = api.register(user, pw, key_pair['public'])['token']
    return mainMenu.select_action()


def load_keys():
    priv_path = input("Private key path: ")
    pub_path = input("Public key path: ")
    clear_screen()

    with open(priv_path, "rb") as priv_file:
        priv_key = serialization.load_pem_private_key(priv_file.read(), password=None)

    with open(pub_path, "rb") as pub_file:
        pub_key = serialization.load_pem_public_key(pub_file.read())

    return {'private': priv_key, 'public': pub_key}


def action_upload_file():
    file_path = input("File path: ")
    file = open(file_path, 'rb')

    payload = encrypt_file(file.read(), 1, key_pair)

    api.upload_file(token, payload['edata'], payload['ekey'], payload['version'], payload['sign'])


def clear_screen():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')


startMenu = SelectMenu()

registerMenu = SelectMenu({
    '1. Generate a new RSA key pair': lambda: action_register('generate'),
    '2. Select an already existing RSA key pair': lambda: action_register('load'),
    '0. Back': startMenu.select_action
})

startMenu = SelectMenu({
    '1. Register': lambda: registerMenu.select_action("Key Selection"),
    '2. Login': action_login,
    '0. Exit': exit
})

mainMenu = SelectMenu({
    '1. Upload file': action_upload_file,
    '2. Download file': lambda: print("CONA"),
    '0. Exit': exit
})

clear_screen()
startMenu.select_action()


"""
def main(args: list):
    data = b'Faz o PHP Manel!'
    version = b'1'

    to_send = encrypt_PGP_AES_GCM(data, version)
    print(f"\nClient PGP Encryption:\n- edata: {to_send[0]}\n- ekey: {to_send[1]}")
    print(f"- version: {to_send[2]}\n- signature: {to_send[3]}")

    received_data = decrypt_PGP_AES_GCM(to_send[0], to_send[1])
    print(f"\nClient PGP Decryption:\n- {received_data}\n")



if __name__ == "__main__":
    main(argv)
"""
