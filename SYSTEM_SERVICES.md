# System Services

## Logs Server

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

### Services to Client Machines

- `register_user`: Registers a user in the system.<br>
Receives a *username*, a *password* and the clients *public key*.<br>
The *username* must be unique and the *public key* valid.<br>
Returns a *token* for the session.

- `login_user`: Authenticates and starts a session with the user.<br>
Receives a *username* and a *password*.<br>
Returns a *token* for the session.

- `upload_file`: Submits a new file to the system to be stored by the Files Server.<br>
User must be logged in to call this service.<br>
Receives the *encrypted file*, a list of *encrypted keys* to the file, the *version* of the file, the user *signed digest* of the previous three arguments and a *list of usernames* that can contribute to the file (including the user).<br>
The *version* must be equal to 1.<br>
Returns the new *file ID*.

- `update_file`: Updates a file in the system.<br>
User must be logged in to call this service.<br>
Receives the *encrypted file*, a list of *encrypted keys* to the file, the *version* of the file, the user *signed digest* of the previous three arguments, a *list of usernames* of the contributors (including the user) and the *file ID*.

- `get_file`: Retrieves a file from the File Server to a user that has access to it.<br>
User must be logged in to call this service.<br>
Receives a *file ID*.<br>
Returns the requested *file data*, *file key* for the user and file *version*.

- `get_files`: Retrives the files associated with the user from the File Server.<br>
User must be logged in to call this service.<br>
Returns the *file names* and the *file IDs* for the user.

- `report_file`: Signals the Log Server of a failed atempt to process a file.<br>
User must be logged in to call this service.<br>
Receives the *file ID*.

- `get_users`: Retrieves the users associated with a given file.<br>
User must be logged in to call this service.<br>
Receives a *file_id*.<br>
Returns the *usernames* and *public keys* of the users that can contribute to that file.

- `get_user`: Retrieves the user with the given username.<br>
User must be logged in to call this service.<br>
Receives a *username*.<br>
Returns the *username* and *public key* of the user that user.

**Extra services**

- `add_contributors`: Adds a list of contributors to a file.<br>
User must be logged in to call this service.<br>
Receives a *file ID* and a list of *usernames*.

- `remove_contributors`: Removes a list of contributors to a file.<br>
User must be logged in to call this service.<br>
Receives a *file ID* and a list of *usernames*.

## Files Server

| REST Call       | URLs                           | Method |
| :-------------- | :----------------------------- | :----- |
| `upload_file`   | `api/files/`                   | POST   |
| `update_file`   | `api/files/<fid>/`             | PUT    |
| `get_file`      | `api/files/<fid>/users/<uid>/` | GET    |
| `recover_data`  | `api/data/recover/<bsid>/`     | GET    |
| `get_data`      | `api/data/`                    | GET    |

### Services to Logs Server

- `upload_file`: Submits a new file to the system to be stored.<br>
Receives the *encrypted file*, a list of *encrypted keys* to the file and a list of *user IDs* that can contribute to the file.<br>
Returns the new *file ID*.

- `update_file`: Updates a file in the system.<br>
Receives the *file ID*, the *encrypted file*, a list of *encrypted keys* to the file and a *list of user IDs* that can contribute to the file.

- `get_file`: Retrieves a file in the system.<br>
Receives a *file ID* and a *user ID*.<br>
Returns the requested *file data* and *file key* for the user.

- `recover_data`: Performs a full recovery of the data contained within the Files Server.<br>
Receives a *Backup Server ID*.

### Services to Backup Servers

- `get_data`: Retrieves all the data stored in the Files Server.<br>
Returns the *files data*.

## Backup Servers

| REST Call       | URLs                           | Method |
| :-------------- | :----------------------------- | :----- |
| `backup_data`   | `api/data/backup/`             | GET    |
| `get_data`      | `api/data/`                    | GET    |

### Services to Logs Server

- `backup_data`: Performs a full backup of the data in the Files Server.<br>
Only successful if all storage integrity checks pass.<br>
Receives the Logs Server *log data*.<br>
Returns the *Backup Server ID* and a *completion status* of the backup.

### Services to Files Server

- `get_data`: Retrieves the backup files data from a Backup Server.<br>
Returns the stored *backup files data*.
