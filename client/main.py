#!/usr/bin/env python3

from sys import argv
from getpass import getpass
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import serialization

import api
import utils
from selectmenu import SelectMenu
from encryption import generate_RSA_keys, encrypt_file, decrypt_file


DEFAULT_PRIV_PATH = 'private.pem'


token = str()
key_pair = dict()
username = str()


def action_login():
    global token, key_pair, username
    key_pair = load_keys()

    print(utils.bold("Login\n"))
    username = input("Username: ")
    pw = getpass("Password: ")
    utils.clear_screen()

    token = api.login(username, pw)["token"]
    return mainMenu.select_action()


def action_register(key_method):
    global token, key_pair, username
    if key_method == 'generate':
        key_pair = generate_RSA_keys()
        with open(input(f"Save private key as (empty for {DEFAULT_PRIV_PATH}): "), "wb") as f:
            f.write(
                key_pair['private'].private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
    elif key_method == 'load':
        key_pair = load_keys()
    else:
        raise RuntimeError("Something went wrong when choosing the key method")

    username = input("Username: ")
    password = getpass("Password: ")
    if password != getpass("Confirm Password: "):
        raise ValueError("Passwords don't have the same value")
    utils.clear_screen()

    token = api.register(username, password, key_pair['public'])['token']
    return mainMenu.select_action()


def action_upload_file():
    utils.clear_screen()
    print(utils.bold('Upload File -> Select File\n'))
    file_path = input("File path: ")
    utils.clear_screen()

    pubkeys = [key_pair['public']]
    contributors = [username]
    if SelectMenu(['Yes', 'No']).select('Do you want to add contributors to your file?') == 'Yes':
        while True:
            contributor = input('Username (empty to done): ')
            if contributor == '':
                break
            pubkeys.append(api.user_pubkey(token, contributor)['pubkey'])
            contributors.append(contributor)
    utils.clear_screen()

    with open(file_path, "rb") as file:
        edata = encrypt_file(file.read(), 1, key_pair['private'], pubkeys)

    api.upload_file(token, edata['efile'], edata['sign'], edata['ekeys'], contributors)
    print("Success: File Uploaded!")
    return mainMenu.select_action()


def action_download_file(selected_file=None):
    file_id = select_file()['id'] if selected_file == None else selected_file

    response = api.download_file(token, file_id)

    try:
        file_bytes = decrypt_file(response['file'], response['key'], key_pair['private'])
    except InvalidTag:  # If edata, nonce or aes key were changed
        response = api.report_file(token, file_id)
        if response['status'] == 202:
            SelectMenu(
                message='The server rollbacked and the file you select may or may not have changed.\n' +
                        'Please select your file again.',
                choices=['Ok']
            ).select()
            return action_download_file()
        raise RuntimeError(f"Error: Expecting 202 and got {response['status']}. Please report this.")

    with open(input("Save as: "), "wb") as file:
        file.write(file_bytes)
    utils.clear_screen()

    print("Success: File Downloaded!")
    return mainMenu.select_action()


def action_update_file():
    file_selected = select_file()
    if file_selected['contributor'] != username:
        option = SelectMenu(
            message='You were not the last contributor to update the file. Are you sure you want to proceed?',
            choices=[
                'Yes. Overwrite and update now.',
                'No. Download first and update it later.'
            ],
        ).select_index()

        if option == 1:  # Choose to download first
            utils.clear_screen()
            return action_download_file(selected_file=file_selected['id'])

    public_keys = []
    contributors = []
    for c in api.file_contributors(token, file_selected['id']):
        public_keys.append(c['pubkey'])
        contributors.append(c['username'])

    utils.clear_screen()
    file_path = input("File path: ")
    utils.clear_screen()

    with open(file_path, "rb") as file:
        edata = encrypt_file(file.read(), file_selected['version']+1, key_pair['private'], public_keys)

    api.update_file(token, file_selected['id'], edata['efile'], edata['sign'],
                    edata['version'], edata['ekeys'], contributors)

    print("Success: File Updated!")
    return mainMenu.select_action()


def action_list_files():
    utils.clear_screen()
    file_list = api.list_files(token)
    print("Files List\n")
    for file in file_list:
        print(file_details(file))

    input("\nPress any key to go back to the menu...")
    utils.clear_screen()
    return mainMenu.select_action()


def action_exit():
    utils.clear_screen()
    print("Thank you for using the best project of SIRS!")
    print("Have a great day :)")
    print("\n")
    print("Exited successfully!")
    exit(0)


def select_file():
    file_list = api.list_files(token)

    menu = SelectMenu([file_details(file) for file in file_list] + ['0. Back'])
    selected = menu.select_index(message='Select your file', clear_before=True)
    if selected == len(file_list):
        return mainMenu.select_action(clear_before=True)

    return file_list[selected]


def file_details(file: dict) -> str:
    return f"ID: {file['id']} | Name: {file['name']} | Size: {file['size']} bytes | Last updated by: {file['contributor']}"


def load_keys():
    utils.clear_screen()
    priv_path = input(f"Private key path (empty for {DEFAULT_PRIV_PATH}): ")
    if priv_path == '':
        priv_path = DEFAULT_PRIV_PATH

    utils.clear_screen()

    with open(priv_path, "rb") as priv_file:
        priv_key = serialization.load_pem_private_key(priv_file.read(), password=None)

    return {'private': priv_key, 'public': priv_key.public_key()}


registerMenu = SelectMenu({
    '1. Generate a new RSA key pair': lambda: action_register('generate'),
    '2. Select an already existing RSA key pair': lambda: action_register('load'),
    '0. Back': lambda: startMenu.select_action(clear_before=True)
}, message="Select your key...")


startMenu = SelectMenu({
    '1. Register': lambda: registerMenu.select_action(clear_before=True),
    '2. Login': action_login,
    '0. Exit': action_exit
}, message="SIRS T01 : Ransomware Protection Project")

mainMenu = SelectMenu({
    '1. Upload file': action_upload_file,
    '2. Download file': action_download_file,
    '3. Update file': action_update_file,
    '4. List files': action_list_files,
    '0. Exit': action_exit
}, message="Main Menu")

utils.clear_screen()


def dev():
    global token, username, key_pair
    username = 'rickerp'
    token = api.login(username, 'pass1234')["token"]
    with open('private.pem', "rb") as priv_file:
        priv_key = serialization.load_pem_private_key(priv_file.read(), password=None)
        key_pair = {'private': priv_key, 'public': priv_key.public_key()}

    mainMenu.select_action()


startMenu.select_action() if len(argv) == 1 else dev()
