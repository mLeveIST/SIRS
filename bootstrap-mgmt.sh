#!/usr/bin/env bash

sudo apt-get update
sudo ln -sf /usr/share/zoneinfo/UTC /etc/localtime
# install tools for managing ppa repositories
sudo apt-get -y install software-properties-common
sudo apt-get -y install unzip
sudo apt-get -y install build-essential 
sudo apt-get -y libssl-dev 
sudo apt-get -y libffi-dev 
sudo apt-get -y python-dev 
sudo apt-get -y python-pip 
sudo apt-get -y python3-pip

# Add graph builder tool for Terraform
sudo apt-get -y install graphviz

# install ansible (http://docs.ansible.com/intro_installation.html)
apt-add-repository -y ppa:ansible/ansible
sudo apt-get update
sudo apt-get -y install ansible

sudo apt-get update && sudo apt-get upgrade -y

# install key
cat /vagrant/control/id_rsa.pub >> /home/vagrant/.ssh/authorized_keys

# configure hosts file for the internal network defined by Vagrantfile
cat >> /etc/hosts <<EOL

# vagrant environment nodes
192.168.56.10   mgmt
192.168.57.10   log
192.168.57.13   file
192.168.57.11   bs1
192.168.57.12   bs2
192.168.59.11   client1
192.168.59.12   client2
192.168.59.13   client3
192.168.53.10   attacker
EOL
