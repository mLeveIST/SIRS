#!/usr/bin/env python3

from sys import argv
from getpass import getpass
from typing import Callable
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import serialization

import api
from utils import clear_screen, clear_before, bold, ServerException, is_client_error
from selectmenu import SelectMenu
from encryption import generate_RSA_keys, encrypt_file, decrypt_file


DEFAULT_PRIV_PATH = 'private.pem'


token = str()
key_pair = dict()
username = str()


def action_login():
    global token, key_pair, username

    try:
        key_pair = load_keys()
    except (FileNotFoundError, ValueError) as e:
        if isinstance(e, FileNotFoundError):
            return errorMenu(f"{e.strerror} : {e.filename}.", action_login, startMenu.select_action).select_action()
        elif isinstance(e, ValueError):
            return errorMenu(f"File not a valid RSA private key.", action_login, startMenu.select_action).select_action()

    clear_screen()
    print(bold("Login\n"))
    username = input("Username: ")
    pw = getpass("Password: ")

    try:
        response = api.login(username, pw)
        token = response["token"]
        if response.get('role', 'user') == 'staff':
            global mainMenu
            mainMenu = SelectMenu(
                mainMenu.choices[:-1] + ['5. Backup files'] + mainMenu.choices[-1:],
                mainMenu.actions[:-1] + [action_backup] + mainMenu.actions[-1:],
                message='Main Menu (Admin)'
            )
    except ServerException as e:
        if is_client_error(e.status):
            return errorMenu(e.error_message, action_login, startMenu.select_action).select_action()
        else:
            raise e

    clear_screen()
    return mainMenu.select_action()


def action_register(key_method):
    global token, key_pair, username
    if key_method == 'generate':
        key_pair = generate_RSA_keys()
        priv_path = input(f"Save private key as (empty for {DEFAULT_PRIV_PATH}): ")
        if priv_path == '':
            priv_path = DEFAULT_PRIV_PATH
        with open(priv_path, "wb") as f:
            f.write(
                key_pair['private'].private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
    elif key_method == 'load':
        try:
            key_pair = load_keys()
        except (FileNotFoundError, ValueError) as e:
            if isinstance(e, FileNotFoundError):
                return errorMenu(f"{e.strerror} : {e.filename}", action_login, startMenu.select_action).select_action()
            elif isinstance(e, ValueError):
                return errorMenu("File not a valid RSA private key.", action_login, startMenu.select_action).select_action()

    while True:
        clear_screen()
        print(bold("Register\n"))
        username = input("Username: ")
        password = getpass("Password: ")
        if password != getpass("Confirm Password: "):
            menu = errorMenu("Passwords must match.", clear_screen, startMenu.select_action)
            if menu.select_index() == 1:
                return menu.actions[1]()
            continue
        break

    try:
        token = api.register(username, password, key_pair['public'])['token']
    except ServerException as e:
        if is_client_error(e.status):
            clear_screen()
            return errorMenu(
                e.error_message,
                lambda: action_register(key_method),
                startMenu.select_action
            ).select_action()
        else:
            raise e

    clear_screen()
    return mainMenu.select_action()


def action_upload_file():
    clear_screen()
    print(bold('Upload File -> Select File\n'))
    try:
        with open(input("File path: "), "rb") as file:
            file_bytes = file.read()
    except FileNotFoundError as e:
        return errorMenu(f"Error: {e.strerror} : {e.filename}", action_upload_file, mainMenu.select_action).select_action()

    clear_screen()

    pubkeys = [key_pair['public']]
    contributors = [username]
    if SelectMenu(['Yes', 'No']).select('Do you want to add contributors to your file?') == 'Yes':
        while True:
            contributor = input('Username (empty to done): ')
            if contributor == '':
                break

            try:
                pubkeys.append(api.user_pubkey(token, contributor)['pubkey'])
            except ServerException as e:
                if is_client_error(e.status):
                    print(f"Error: {e.error_message}")
                    continue
                else:
                    raise e

            contributors.append(contributor)

    clear_screen()

    edata = encrypt_file(file_bytes, 1, key_pair['private'], pubkeys)

    try:
        api.upload_file(token, edata['efile'], edata['sign'], edata['ekeys'], contributors)
    except ServerException as e:
        if is_client_error(e.status):
            return errorMenu(e.error_message, action_upload_file, mainMenu.select_action).select_action()
        else:
            raise e

    print("Success: File Uploaded!")
    return mainMenu.select_action()


def action_download_file(selected_file=None):
    file_id = select_file()['id'] if selected_file == None else selected_file

    try:
        response = api.download_file(token, file_id)
    except ServerException as e:
        if is_client_error(e.status):
            return errorMenu(e.error_message, action_download_file, mainMenu.select_action).select_action()
        else:
            raise e

    try:
        file_bytes = decrypt_file(response['file'], response['key'], key_pair['private'])
    except InvalidTag:  # If edata, nonce or aes key were changed
        api.report_file(token, file_id)
        SelectMenu(
            message='The server rollbacked and the file you select may or may not have changed.\n' +
                    'Please select your file again.',
            choices=['Ok']
        ).select()
        return action_download_file()

    with open(input("Save as: "), "wb") as file:
        file.write(file_bytes)
    clear_screen()

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
            clear_screen()
            return action_download_file(selected_file=file_selected['id'])

    try:
        response = api.file_contributors(token, file_selected['id'])
    except ServerException as e:
        if is_client_error(e.status):
            return errorMenu(e.error_message, action_update_file, mainMenu.select_action).select_action()
        else:
            raise e

    public_keys = []
    contributors = []
    for c in response:
        public_keys.append(c['pubkey'])
        contributors.append(c['username'])

    clear_screen()
    while True:
        file_path = input("File path: ")
        try:
            with open(file_path, "rb") as file:
                edata = encrypt_file(file.read(), file_selected['version']+1, key_pair['private'], public_keys)
            break
        except FileNotFoundError as e:
            eMenu = errorMenu(f"Error: {e.strerror} : {e.filename}", clear_screen, mainMenu.select_action)
            if eMenu.select_index == 1:
                return eMenu.actions[1]()
            eMenu.actions[0]()
            print('Error: File not found\n')

    try:
        api.update_file(token, file_selected['id'], edata['efile'], edata['sign'],
                        edata['version'], edata['ekeys'], contributors)
    except ServerException as e:
        if is_client_error(e.status):
            return errorMenu(e.error_message, action_update_file, mainMenu.select_action).select_action()
        else:
            raise e

    clear_screen()
    print("Success: File Updated!")
    return mainMenu.select_action()


def action_list_files():
    clear_screen()

    try:
        file_list = api.list_files(token)
    except ServerException as e:
        if is_client_error(e.status):
            return errorMenu(e.error_message, action_list_files, mainMenu.select_action).select_action()
        else:
            raise e

    print(bold("Files List\n"))
    for file in file_list:
        print(file_details(file))

    input(bold("\nPress any key to go back to the menu..."))
    clear_screen()
    return mainMenu.select_action()


def action_backup():
    try:
        api.backup_files(token)
    except ServerException as e:
        if is_client_error(e.status):
            return errorMenu(e.error_message, action_backup, mainMenu.select_action).select_action()
        else:
            raise e

    clear_screen()
    print("Backup succeeded!")
    return mainMenu.select_action()


def action_exit():
    clear_screen()
    print("Thank you for using the best project of SIRS!")
    print("Have a great day :)")
    print("\n")
    print(bold("Exited successfully!"))
    exit(0)


def select_file():
    try:
        file_list = api.list_files(token)
    except ServerException as e:
        if is_client_error(e.status):
            return errorMenu(e.error_message, select_file, mainMenu.select_action).select_action()
        else:
            raise e

    menu = SelectMenu([file_details(file) for file in file_list] + ['0. Back'])
    clear_screen()
    selected = menu.select_index(message='Select your file')
    if selected == len(file_list):
        clear_screen()
        return mainMenu.select_action()

    return file_list[selected]


def file_details(file: dict) -> str:
    return f"ID: {file['id']} | Name: {file['name']} | Size: {file['size']} bytes | Last updated by: {file['contributor']}"


def load_keys():
    clear_screen()
    priv_path = input(f"Private key path (empty for {DEFAULT_PRIV_PATH}): ")
    if priv_path == '':
        priv_path = DEFAULT_PRIV_PATH

    clear_screen()

    with open(priv_path, "rb") as priv_file:
        priv_key = serialization.load_pem_private_key(priv_file.read(), password=None)

    return {'private': priv_key, 'public': priv_key.public_key()}


def errorMenu(message: str, again_action: Callable, back_action: Callable):
    print('')
    return SelectMenu(
        message=f"Error: {message}",
        choices={'1. Try again': again_action, '2. Go back': lambda: clear_before(back_action)}
    )


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

clear_screen()


def dev():
    global token, username, key_pair
    username = 'rickerp'
    token = api.login(username, 'pass1234')["token"]
    with open('private.pem', "rb") as priv_file:
        priv_key = serialization.load_pem_private_key(priv_file.read(), password=None)
        key_pair = {'private': priv_key, 'public': priv_key.public_key()}

    mainMenu.select_action()


startMenu.select_action() if len(argv) == 1 else dev()
