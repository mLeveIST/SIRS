#!/usr/bin/env python3

from sys import argv
from cryptography.hazmat.primitives import serialization
from selectmenu import SelectMenu
from getpass import getpass

import api
import utils
from encryption import generate_RSA_keys, encrypt_file, decrypt_file


DEFAULT_PRIV_PATH = 'private.pem'


token = None
key_pair = None


def action_login():
    global token, key_pair
    key_pair = load_keys()

    user = input("Username: ")
    pw = getpass("Password: ")
    utils.clear_screen()

    token = api.login(user, pw)["token"]
    return mainMenu.select_action("Main Menu")


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
    utils.clear_screen()

    token = api.register(user, pw, key_pair['public'])['token']
    return mainMenu.select_action("Main Menu")


def action_upload_file():
    file_path = input("File path: ")
    utils.clear_screen()
    with open(file_path, "rb") as file:
        edata = encrypt_file(file.read(), 1, key_pair)

    api.upload_file(token, edata['efile'], edata['ekey'], edata['sign'])
    print("Success: File Uploaded!")
    return mainMenu.select_action("Main Menu")


def action_download_file():
    file_id = select_file()['id']

    response = api.download_file(token, file_id)
    file_bytes = decrypt_file(response['efile'], response['ekey'], key_pair)

    with open(input("Save as: "), "wb") as file:
        file.write(file_bytes)
    utils.clear_screen()
    print("Success: File Downloaded!")
    return mainMenu.select_action("Main Menu")


def action_update_file():
    file_path = input("File path: ")
    utils.clear_screen()
    with open(file_path, "rb") as file:
        file_selected = select_file()
        edata = encrypt_file(file.read(), file_selected['version']+1, key_pair)

    response = api.update_file(
        token, file_selected['id'], edata['efile'], edata['ekey'], edata['version'], edata['sign'])

    print("Success: File Updated!")
    return mainMenu.select_action("Main Menu")


def action_list_files():
    utils.clear_screen()
    file_list = api.list_files(token)
    print("Files List\n")
    for file in file_list:
        print('ID: {} | Name: {} | Size: {} bytes'.format(file['id'], file['name'], file['size']))

    input("\nPress any key to go back to the menu...")
    utils.clear_screen()
    return mainMenu.select_action("Main Menu")


def action_exit():
    utils.clear_screen()
    print("Thank you for using the best project for SIRS!")
    print("Have a great day :)")
    print("\n")
    print("Exited successfully!")
    exit(0)


def select_file():
    file_list = api.list_files(token)
    menu = SelectMenu(['ID: {} | Name: {} | Size: {} bytes'.format(
        file['id'], file['name'], file['size']) for file in file_list])
    return file_list[menu.select_index()]


def load_keys():
    priv_path = input("Private key path (empty for {}): ".format(DEFAULT_PRIV_PATH))
    if priv_path == '':
        priv_path = DEFAULT_PRIV_PATH

    utils.clear_screen()

    with open(priv_path, "rb") as priv_file:
        priv_key = serialization.load_pem_private_key(priv_file.read(), password=None)

    return {'private': priv_key, 'public': priv_key.public_key()}


startMenu = SelectMenu()

registerMenu = SelectMenu({
    '1. Generate a new RSA key pair': lambda: action_register('generate'),
    '2. Select an already existing RSA key pair': lambda: action_register('load'),
    '0. Back': startMenu.select_action
})

startMenu = SelectMenu({
    '1. Register': lambda: registerMenu.select_action("RSA Encryption Key"),
    '2. Login': action_login,
    '0. Exit': action_exit
})

mainMenu = SelectMenu({
    '1. Upload file': action_upload_file,
    '2. Download file': action_download_file,
    '3. Update file': action_update_file,
    '4. List files': action_list_files,
    '0. Exit': action_exit
})

utils.clear_screen()
startMenu.select_action()
