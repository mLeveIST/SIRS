# API

## Log Server

| REST Call         | URLs                       | Method |
| :---------------- | :------------------------- | :----- |
| `register_user`   | `api/users/register/`      | POST   |
| `login_user`      | `api/users/login/`         | POST   |
| `upload_file`\*   | `api/files/`               | POST   |
| `update_file`\*\* | `api/files/<fid>/`         | PUT    |
| `get_file`\*\*    | `api/files/<fid>/`         | GET    |
| `get_files`\*     | `api/files/`               | GET    |
| `report_file`     | `api/files/<fid>/report/`  | GET    |
| `get_users`       | `api/files/<fid>/users/`   | GET    |
| `get_user`        | `api/users/<str:username>` | GET    |

###### \* In practice, the used call is `files_detail`.

###### \*\* In practice, the used call is `file_detail`.

&ensp;

### Available for clients

- `register_user`: Registers a user in the system.<br>
  Receives a _username_, a _password_ and the clients _public key_.<br>
  The _username_ must be unique and the _public key_ valid.<br>
  Returns a _token_ for the session.

- `login_user`: Authenticates and starts a session with the user.<br>
  Receives a _username_ and a _password_.<br>
  Returns a _token_ for the session.

- `upload_file`: Submits a new file to the system to be stored by the Files Server.<br>
  User must be logged in to call this service.<br>
  Receives the _encrypted file_, a list of _encrypted keys_ to the file, the _version_ of the file, the user _signed digest_ of the previous three arguments and a _list of usernames_ that can contribute to the file (including the user).<br>
  The _version_ must be equal to 1.<br>
  Returns the new _file ID_.

- `update_file`: Updates a file in the system.<br>
  User must be logged in to call this service.<br>
  Receives the _encrypted file_, a list of _encrypted keys_ to the file, the _version_ of the file, the user _signed digest_ of the previous three arguments, a _list of usernames_ of the contributors (including the user) and the _file ID_.

- `get_file`: Retrieves a file from the File Server to a user that has access to it.<br>
  User must be logged in to call this service.<br>
  Receives a _file ID_.<br>
  Returns the requested _file data_, _file key_ for the user and file _version_.

- `get_files`: Retrives the files associated with the user from the File Server.<br>
  User must be logged in to call this service.<br>
  Returns the _file names_ and the _file IDs_ for the user.

- `report_file`: Signals the Log Server of a failed atempt to process a file.<br>
  User must be logged in to call this service.<br>
  Receives the _file ID_.

- `get_users`: Retrieves the users associated with a given file.<br>
  User must be logged in to call this service.<br>
  Receives a _file_id_.<br>
  Returns the _usernames_ and _public keys_ of the users that can contribute to that file.

- `get_user`: Retrieves the user with the given username.<br>
  User must be logged in to call this service.<br>
  Receives a _username_.<br>
  Returns the _username_ and _public key_ of the user that user.

**Extra services** - For future developments

- `add_contributors`: Adds a list of contributors to a file.<br>
  User must be logged in to call this service.<br>
  Receives a _file ID_ and a list of _usernames_.

- `remove_contributors`: Removes a list of contributors to a file.<br>
  User must be logged in to call this service.<br>
  Receives a _file ID_ and a list of _usernames_.

## File Server

| REST Call      | URLs                           | Method |
| :------------- | :----------------------------- | :----- |
| `upload_file`  | `api/files/`                   | POST   |
| `update_file`  | `api/files/<fid>/`             | PUT    |
| `get_file`     | `api/files/<fid>/users/<uid>/` | GET    |
| `recover_data` | `api/data/recover/<bsid>/`     | GET    |
| `get_data`     | `api/data/`                    | GET    |

&ensp;

### Available for log server

- `upload_file`: Submits a new file to the system to be stored.<br>
  Receives the _encrypted file_, a list of _encrypted keys_ to the file and a list of _user IDs_ that can contribute to the file.<br>
  Returns the new _file ID_.

- `update_file`: Updates a file in the system.<br>
  Receives the _file ID_, the _encrypted file_, a list of _encrypted keys_ to the file and a _list of user IDs_ that can contribute to the file.

- `get_file`: Retrieves a file in the system.<br>
  Receives a _file ID_ and a _user ID_.<br>
  Returns the requested _file data_ and _file key_ for the user.

- `recover_data`: Performs a full recovery of the data contained within the Files Server.<br>
  Receives a _Backup Server ID_.

### Available for Backup Servers

- `get_data`: Retrieves all the data stored in the Files Server.<br>
  Returns the _files data_.

&ensp;

## Backup Servers

| REST Call     | URLs               | Method |
| :------------ | :----------------- | :----- |
| `backup_data` | `api/data/backup/` | POST   |
| `get_data`    | `api/data/`        | GET    |

&ensp;

### Services to Logs Server

- `backup_data`: Performs a full backup of the data in the Files Server.<br>
  Only successful if all storage integrity checks pass.<br>
  Receives the Logs Server _log data_.<br>
  Returns the _Backup Server ID_ and a _completion status_ of the backup.

### Services to Files Server

- `get_data`: Retrieves the backup files data from a Backup Server.<br>
  Returns the stored _backup files data_.
