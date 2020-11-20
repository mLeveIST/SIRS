# System Services

## Logs Server

### Services to Client Machines

- `register_user`: Registers a user in the system.<br>
Receives a *username*, a *password* and a *certificate* for its public key.<br>
The *username* must be unique and the *certificate* valid.<br>
Returns a *token* for the session.

- `login_user`: Authenticates and starts a session with the user.<br>
Receives a *username* and a *password*.<br>
Returns a *token* for the session.

- `create_file`: Submits a new file to the system to be stored by the Files Server.<br>
User must be logged in to call this service.<br>
Receives the *encrypted file*, a list of *encrypted keys* to the file, the *version* of the file, the user *signed digest* of the previous three arguments and a *list of usernames* that can contribute to the file.<br>
Returns the new *file ID*.

- `update_file`: Updates a file in the system.<br>
User must be logged in to call this service.<br>
Receives the *encrypted file*, a list of *encrypted keys* to the file, the *version* of the file, the user *signed digest* of the previous three arguments and the *file ID*.

- `get_file`: Retrieves a file from the File Server to a user that has access to it.<br>
User must be logged in to call this service.<br>
Receives a *file ID*.<br>
Returns the requested *file data* and *file key* for the user.

- `get_user_certificates`: Retrieves the specified users in the system.<br>
User must be logged in to call this service.<br>
Receives a *list of usernames*.<br>
Returns the *certificates* of the requested usernames.

**Extra services**

- `add_contributors`: Adds a list of contributors to a file.<br>
User must be logged in to call this service.<br>
Receives a *file ID* and a list of *usernames*.

- `remove_contributors`: Removes a list of contributors to a file.<br>
User must be logged in to call this service.<br>
Receives a *file ID* and a list of *usernames*.

## Files Server

### Services to Logs Server

- `create_file`: Submits a new file to the system to be stored.<br>
Receives the *user ID*, *encrypted file*, a list of *encrypted keys* to the file and a *list of user IDs* that can contribute to the file.<br>
Returns the new *file ID*.

- `update_file`: Updates a file in the system.<br>
Receives the *user ID*, the *file ID*, the *encrypted file* and a list of *encrypted keys* to the file.

- `get_file`: Retrieves a file in the system.<br>
Receives a *user ID* and a *file ID*.<br>
Returns the requested *file data* and *file key* for the user.

- `recover_data`: Performs a full recovery of the data contained within the Files Server.<br>
Receives a *Backup Server ID*.

### Services to Backup Servers

- `get_data`: Retrieves all the data stored in the Files Server.<br>
Returns the stored data.

## Backup Servers

### Services to Logs Server

- `backup_data`: Performs a full backup of the data in the Files Server.<br>
Only successful if all storage integrity checks pass.<br>
Receives the Logs Server *log data*.<br>
Returns the *Backup Server ID*, a *completion status* of the backup and a *timestamp* of the last backup.

### Services to Files Server

- `get_data`: Retrieves the backup data from a Backup Server, rolling back the file system state.<br>
Returns the stored *backup data*.
