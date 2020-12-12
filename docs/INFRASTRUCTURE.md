# Infrastructure

This is the setup guide for the correct deployment
of the infrastructure necessary for this project.

## Directory Structure

First, confirm the directory has the following top level
structure:<br>
```
.
├── backupserver1
├── backupserver2
├── client
├── control
├── fileserver
├── logserver
├── provisioning
├── Vagrantfile

```

### Install vagrant (and plugins) and virtualbox
Second, confirm you have installed vagrant 
and virtualbox. We used the following versions:<br>
##### - Vagrant 2.2.6<br>
##### - 6.1.10_Ubuntur138449 VBOX<br>

#### Install vagrant plugin
`vagrant plugin install vagrant-vbguest`<br>

### Checking the environment
Third, confirm that when running the command
`vagrant status` in the project directory
that the output is as such:

![](infrastructure/assets/vagrant_status_initial.png)

## Setting up the environment

### Creating Virtual Machines

First, run the command `vagrant up` as this will
start to create the VM's and provision them according
to their provision script. 
This will take a couple of minutes (approx. 15).
It will create the following VMs:

- `mgmt`: This VM is not part of the service, being
its sole purpose is to be the Management Node. It's from
this VM, in the guest's `control` directory, that the ansible scripts will be run which,
in turn, will provide the other VM's with most modules
and configurations needed.
  
- `log`: This VM is where the *Log Server* will be configured.
It is provisioned by the script `bootstrap-logserver.sh`
and it has configured a shared folder from the host's `logserver`
directory to the guest's `/var/repo/logserver` with permissions
and ownership necessary for *apache2*.

- `file`: This VM is where the *File Server* will be configured.
It is provisioned by the script `bootstrap-fileserver.sh`
and it has configured a shared folder from the host's `fileserver`
directory to the guest's `/var/repo/fileserver` with permissions
and ownership necessary for *apache2*.

- `bs1/bs2`: These VMs are where the *Backup Servers* will be configured.
They are provisioned by the script `bootstrap-backups.sh`
and they have configured a shared folder from the host's `backupserver1` 
and `backupserver2`, depending on if *bs1* or *bs2*, 
directory to the guest's `/var/repo/backupserver` 
with permissions and ownership necessary for *apache2*.

- `client1/client2`: These VMs are where the *Clients* will be configured.
They are provisioned by the script `bootstrap-client.sh`
and they have benn configured a shared folder from the host's `client`
directory to the guest's `/home/vagrant/client`.
  
### Ansible in Management node
After all the `vagrant up` command is finished all
VMs should be running like such when running `vagrant status:

![](./infrastructure/assets/vagrant_running.png)

Confirm your *control* directory has been populated
with the following files:

- `bs1/bs2 .ovpn`: files necessary for the vpn connection afterwards.
These were obtained by utilizing a third-party script found in 
[Nyr/openvpn-install](https://github.com/Nyr/openvpn-install)
just with a line commented out in order to pass input non-interactively.
- `id_rsa/ id_rsa.pub`: keys for the ansible ssh password less setup.
- `rootCA.crt / rootCA.key`: certificate and key for ou abstract CA:
  
Next you need to ssh into the Management Node by doing
`vagrant ssh mgmt`. Change directory into the control shared
folder and start by testing the basic ansible check command
which is `ansible all -m ping`. The response should be
the following:

![](./infrastructure/assets/ansible_ping.png)

#### Important first Steps

##### Password-less connection ssh

While most the steps are automated in our main playbook
**all_playbooks.yaml**, some steps have to be run first
otherwise some errors can occur.

Next playbook to run has to be *ssh-addkey.yaml* with
the option *--ask-pass* which will then prompt for a password,
being the default password that
was used **vagrant**. Run the command 
`ansible-playbook ssh-addkey.yaml --ask-pass`.
The output should be the following:

![](./infrastructure/assets/ansible_sshkey.png)

##### Configure VPN between *File Server* and *Backup Servers*

After the playbook for the vpn has to be run with the command
`ansible-playbook vpn.yaml`. This will install openvpn
and insert and config file in the *Backup Servers*.

![](./infrastructure/assets/ansible_vpn_play.png)

Now it is needed to ssh into both *Backup Servers* by
doing `vagrant ssh bs1` and `vagrant ssh bs2`. Here 2
commands have to be run in order to configure the vpn.
Here is the example for *bs1* (for *bs2* simply change the number
1 in each command):

- `sudo openvpn --client --config /etc/openvpn/bs1.conf`: You can
quit the command when this state is reached:
  
![](./infrastructure/assets/openvpn_conf.png)

- `sudo systemctl start openvpn@bs1`: After this
by running the command `ip addr show` you can verify
the following interface exists:
  
![](./infrastructure/assets/ip_addr.png)

##### Playbook for module installment

Next the playbook *install.yaml* will install 
python modules and libraries as well apache2 (and 
its dependencies) for the *Log/File/Backup Servers*.
It will also install python module and pip3 in the client
machines. Run the command 
`ansible-playbook install.yaml` 
which will take some time to finish (approx 3-4 min.):

![](./infrastructure/assets/ansible_install.png)

Afterwards it is needed to ssh into *client1* and *client2*
with `vagrant ssh client1` and `vagrant ssh client2`.
There install the python libraries needed with
`pip3 install -r client/requirements.txt`. This has
to be done this way, or an error will occur in another
playbook task.

Confirm if *cacert.pem* exists in folder
`/home/vagrant/.local/lib/python3.6/site-packages/certifi/`
as such:

![](./infrastructure/assets/client_pip3.png)

##### Last Ansible Step

To conclude, the final playbook has to be run
with the command `ansible-playbook all_playbooks.yaml`.
This will 5 playbooks in total which will take some time:

- `add_ca.yaml`: This will install a certificate module
and update said module with our abstract CA certificate.
  
- `nfs.yaml`: This will setup a nfs server in the *File Server*, 
export a "mountable" directory for the *Backup Servers*. It
will also create *symlinks* from this "mountable" directory
to */var/repo/fileserver/ and to */var/repo/backupserver*, in
the *File Server* and *Backup Servers respectively. This will fail
if the *sharedfiles* link exists so make sure to delete it in all
three servers before running. If it is forgotten then remove the *sharedfiles*
and rerun the play *all_plpaybooks.yaml*.
  
- `generate-keys.yaml`: This will create keys and a certificate
signed by our abstract CA in each of the **Servers**.
  
- `dist-crt.yaml`: This will add the abstract CA certificate
to the *cacert.pem* in all VMs.
  
- `build.yaml`: This will copy the apache2 configuration files
and routing to each of the **Servers**.
  
The output should be similar to the following:

![](./infrastructure/assets/ansible_all.png)


### Setting up database and Launching the Server

For this first step go to each server's folder 
(ex: /var/repo/logserver for *Log Server*) in the
guest's machines and run the following commands
(with an example output for the *Log Server*:

- `sudo python3 manage.py makemigrations api`
  
![](./infrastructure/assets/makemigrations.png)

- `sudo python3 manage.py migrate`

![](./infrastructure/assets/migrate.png)

Finally, either run the command 
`sudo systemctl restart apache2` in each of the
**Servers** or re-run the play *build.yaml* in the
Management Node with `ansible-playbook build.yaml` (recommended).

![](./infrastructure/assets/ansible_build.png)

If everything performed correctly then the infrastructure
has been provided.

# THE END


