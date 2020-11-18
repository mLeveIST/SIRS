#!/usr/bin/env bash

sudo apt-get update
sudo ln -sf /usr/share/zoneinfo/UTC /etc/localtime
# install ansible (http://docs.ansible.com/intro_installation.html)
sudo apt-get -y install software-properties-common
apt-add-repository -y ppa:ansible/ansible
sudo apt-get update
sudo apt-get -y install ansible

# configure hosts file for the internal network defined by Vagrantfile
cat >> /etc/hosts <<EOL

# vagrant environment nodes
192.168.56.10   mgmt
192.168.57.10   log
192.168.57.11   file
192.168.58.11   bs1
192.168.58.12   bs2
192.168.59.11   client1
EOL
