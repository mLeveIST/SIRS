# API

## Log Server

| REST Call               | URLs                       | Method |
| :---------------------- | :------------------------- | :----- |
| `register_user`         | `api/users/register/`      | POST   |
| `login_user`            | `api/users/login/`         | POST   |
| `upload_file`\*         | `api/files/`               | POST   |
| `update_file`\*\*       | `api/files/<fid>/`         | PUT    |
| `download_file`\*\*     | `api/files/<fid>/`         | GET    |
| `list_files`\*          | `api/files/`               | GET    |
| `report_file`           | `api/files/<fid>/report/`  | GET    |
| `get_file_contributors` | `api/files/<fid>/users/`   | GET    |
| `get_user_pubkey`       | `api/users/<str:username>` | GET    |
| `backup_data`.          | `api/files/backup`         | GET    |

###### \* In practice, the used call is `files_detail`.

###### \*\* In practice, the used call is `file_detail`.

&ensp;

### Available for clients

- `register_user`: Registers a user in the system.<br>
  Receives a _username_, a _password_ and the clients _public key_.<br>
  The _username_ must be unique and the _public key_ valid.<br>
  Returns a _token_ for the session.

- `login_user`: Authenticates and starts a session with the user.<br>
Receives a *username* and a *password* and optionaly the *public key*.<br>
Returns a *token* for the session, and an *admin* flag if the user is an admin.

- `upload_file`: Submits a new file to the system to be stored by the Files Server.<br>
  User must be logged in to call this service.<br>
  Receives the _encrypted file_, a list of _encrypted keys_ to the file, the _version_ of the file, the user _signed digest_ of the previous three arguments and a _list of usernames_ that can contribute to the file (including the user).<br>
  The _version_ must be equal to 1.<br>
  Returns the new _file ID_.

- `update_file`: Updates a file in the system.<br>
  User must be logged in to call this service.<br>
  Receives the _encrypted file_, a list of _encrypted keys_ to the file, the _version_ of the file, the user _signed digest_ of the previous three arguments, a _list of usernames_ of the contributors (including the user) and the _file ID_.

- `download_file`: Retrieves a file from the File Server to a user that has access to it.<br>
User must be logged in to call this service.<br>
Receives a *file ID*.<br>
Returns the requested *file data*, *file key* for the user and file *version*.

- `list_files`: Retrives the files associated with the user from the File Server.<br>
User must be logged in to call this service.<br>
Returns the *file names*, the *file IDs*, the *file sizes*, the *versions* and last *contributor* to the user.

- `report_file`: Signals the Log Server of a failed atempt to process a file in a client.<br>
User must be logged in to call this service.<br>
Receives the *file ID*.

- `get_file_contributors`: Retrieves the users associated with a given file.<br>
User must be logged in to call this service.<br>
Receives a *file_id*.<br>
Returns the *usernames* and *public keys* of the users that can contribute to that file.

- `get_user_pubkey`: Retrieves the user with the given username.<br>
User must be logged in to call this service.<br>
Receives a *username*.<br>
Returns the *username* and *public key* of the user that user.

## Files Server

| REST Call       | URLs                           | Method |
| :-------------- | :----------------------------- | :----- |
| `upload_file`   | `api/files/`                   | POST   |
| `update_file`   | `api/files/<fid>/`             | PUT    |
| `dowload_file`  | `api/users/<uid>/files/<fid>/` | GET    |
| `list_files`    | `api/users/<uid>/files/`       | GET    |
| `recover_data`  | `api/data/recover/<bsid>/`     | GET    |
| `get_file_data` | `api/data/<fid>/`              | GET    |
| `get_data`      | `api/data/`                    | GET    |

&ensp;

### Available for log server

- `upload_file`: Submits a new file to the system to be stored.<br>
  Receives the _encrypted file_, a list of _encrypted keys_ to the file and a list of _user IDs_ that can contribute to the file.<br>
  Returns the new _file ID_.

- `update_file`: Updates a file in the system.<br>
  Receives the _file ID_, the _encrypted file_, a list of _encrypted keys_ to the file and a _list of user IDs_ that can contribute to the file.

- `dowload_file`: Retrieves a file in the system.<br>
Receives a *file ID* and a *user ID*.<br>
Returns the requested *file data* and *file key* for the user.

- `list_files`: Retrives the files associated with the user from the File Server.<br>
Returns the *file names*, *file IDs* and the *file sizes*.

- `recover_data`: Performs a full recovery of the data contained within the Files Server.<br>
Receives a *Backup Server ID* to specify from which server to recover from.

- `get_file_data`: Retrives the data for a specified file in the Files Server.<br>
Returns the *file data*.

### Services to Backup Servers

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
Receives the Logs Server *log data*.<br>
Returns a *completion status* of the backup.

### Services to Files Server

- `get_data`: Retrieves the backup files data from a Backup Server.<br>
  Returns the stored _backup files data_.
