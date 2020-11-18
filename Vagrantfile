# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.ssh.insert_key = false
  config.vbguest.auto_update = false
  config.vm.box_check_update = false  

  # create Management (mgmt) node
  config.vm.define "mgmt" do |mgmt_config|
    mgmt_config.vm.box = "ubuntu/trusty64"
    mgmt_config.vm.hostname = "mgmt"
    mgmt_config.vm.network "private_network", ip: "192.168.56.10"
    mgmt_config.vm.provider "virtualbox" do |vb|
      vb.name = "mgmt"
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      vb.memory = "256"
    end # of vb
    # Shared folders
    if Vagrant::Util::Platform.windows? then
      # Configuration SPECIFIC for Windows 10 hosts
      mgmt_config.vm.synced_folder "control", "/home/vagrant/control",
      id: "vagrant-root", ouner: "vagrant", group: "vagrant",
      mount_options: ["dmode=775", "fmode=664"]
    else
      # Configuration for Unix/Linux hosts
      mgmt_config.vm.synced_folder "control", "/home/vagrant/control",
      mount_options: ["dmode=775", "fmode=664"]
    end # of shared folders
    # Provisioning
    mgmt_config.vm.provision "shell", path: "bootstrap-mgmt.sh"
  end # of mgmt_config

  # create Log Server
  config.vm.define "log" do |log_config|
      log_config.vm.box = "ubuntu/trusty64"
      log_config.vm.hostname = "log"
      log_config.vm.network :private_network, ip: "192.168.57.10"
      log_config.vm.network "forwarded_port", guest: 80, host: 8080
      log_config.vm.provider "virtualbox" do |vb|
          vb.name = "log"
          vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
          vb.memory = "256"
      end # of vb
  end # of log_config

  # create File Server
  config.vm.define "file" do |file_config|
      file_config.vm.box = "ubuntu/trusty64"
      file_config.vm.hostname = "file"
      file_config.vm.network :private_network, ip: "192.168.57.11"
      file_config.vm.network "forwarded_port", guest: 80, host: 8081
      file_config.vm.provider "virtualbox" do |vb|
          vb.name = "file"
          vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
          vb.memory = "256"
      end # of vb
  end # of file_config

  (1..2).each do |i|
    config.vm.define "bs#{i}" do |bs_config|
        # Every Vagrant development environment requires a box.
        bs_config.vm.box = "ubuntu/trusty64"
        # Assign a friendly name to this host VM
        bs_config.vm.hostname = "bs#{i}"
        # Create a private network, which allows host-only access to the machine
        bs_config.vm.network "private_network", ip: "192.168.58.1#{i}"
        bs_config.vm.network "forwarded_port", guest: 80, host: 8081 + i
        # Provider-specific configuration so you can fine-tune various
        bs_config.vm.provider "virtualbox" do |vb|
            # Change the VM name/ID in the Hypervisor
            vb.name = "bs#{i}"
            vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
            vb.memory = 256
        end # of vb
    end # of  bs_config
  end # end of loop

  # Create an new instance
  # insert your instructions here:
  (1..1).each do |i|
    config.vm.define "client#{i}" do |client_config|
        # Every Vagrant development environment requires a box.
        client_config.vm.box = "ubuntu/trusty64"
        # Assign a friendly name to this host VM
        client_config.vm.hostname = "client#{i}"
        # Create a private network, which allows host-only access to the machine
        client_config.vm.network "private_network", ip: "192.168.59.1#{i}"
        # Provider-specific configuration so you can fine-tune various
        client_config.vm.provider "virtualbox" do |vb|
            # Change the VM name/ID in the Hypervisor
            vb.name = "client#{i}"
            vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
            vb.memory = 256
        end # of vb
    end # of client_config
  end # end of loop

=begin
  # Create an new instance
  # insert your instructions here:
  config.vm.define "trudy" do |trudy_config|
      # Every Vagrant development environment requires a box.
      trudy_config.vm.box = "ubuntu/trusty64"
      # Assign a friendly name to this host VM
      trudy_config.vm.hostname = "trudy"
      # Create a private network, which allows host-only access to the machine
      trudy_config.vm.network "private_network", ip: "192.168.56.30"
      # Provider-specific configuration so you can fine-tune various
      trudy_config.vm.provider "virtualbox" do |vb|
        # Change the VM name/ID in the Hypervisor
        vb.name = "trudy"
        vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
        vb.memory = 256
      end # of vb
  end # of client_config
=end

end # of config
