## Register as admin

Because this is an administrator action and may only occurr rarely we didn't add this to the client interface.  
So we must run the following commands in the **logserver**.

0. To enter in the logserver machine, run `vagrant ssh log`
1. Go to the django project folder `cd /var/repo/logserver`
2. Run `python3 manage.py createsuperuser`
3. Insert a username and password
4. Done!
