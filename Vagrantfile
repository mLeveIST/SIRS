# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.ssh.insert_key = false
  config.vbguest.auto_update = false
  config.vm.box_check_update = false  

  # create Management (mgmt) node
  config.vm.define "mgmt" do |mgmt_config|
    mgmt_config.vm.box = "ubuntu/bionic64"
    mgmt_config.vm.hostname = "mgmt"
    mgmt_config.vm.network "private_network", ip: "192.168.56.10"
    mgmt_config.vm.provider "virtualbox" do |vb|
      vb.name = "mgmt"
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      vb.memory = "512"
      vb.customize ["modifyvm", :id, "--uart1", "0x3F8", "4"]
      vb.customize ["modifyvm", :id, "--uartmode1", "file", File::NULL]
    end # of vb
    # Shared folders
    if Vagrant::Util::Platform.windows? then
      # Configuration SPECIFIC for Windows 10 hosts
      mgmt_config.vm.synced_folder "control", "/home/vagrant/control",
      id: "vagrant-root", owner: "vagrant", group: "vagrant",
      mount_options: ["dmode=775", "fmode=775"]
    else
      # Configuration for Unix/Linux hosts
      mgmt_config.vm.synced_folder "control", "/home/vagrant/control",
      mount_options: ["dmode=775", "fmode=775"]
    end # of shared folders
    # Provisioning
    mgmt_config.vm.provision "shell", path: "provisioning/bootstrap-mgmt.sh"
    
  end # of mgmt_config

  # create Log Server
  config.vm.define "log" do |log_config|
    log_config.vm.box = "ubuntu/bionic64"
    log_config.vm.hostname = "log"
    log_config.vm.network "private_network", ip: "192.168.57.10"
    log_config.vm.provider "virtualbox" do |vb|
        vb.name = "log"
        vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
        vb.memory = "512"
        vb.customize ["modifyvm", :id, "--uart1", "0x3F8", "4"]
        vb.customize ["modifyvm", :id, "--uartmode1", "file", File::NULL]
    end # of vb
    # Shared folders
    if Vagrant::Util::Platform.windows? then
      # Configuration SPECIFIC for Windows 10 hosts
      log_config.vm.synced_folder "logserver", "/var/repo/logserver",
      id: "vagrant-root", owner: "www-data", group: "www-data",
      mount_options: ["dmode=775", "fmode=775"]
    else
      # Configuration for Unix/Linux hosts
      log_config.vm.synced_folder "logserver", "/var/repo/logserver",
      owner: "www-data", group: "www-data",
      mount_options: ["dmode=775", "fmode=775"]
    end # of shared folders
    # Provisioning
    log_config.vm.provision "shell", path: "provisioning/bootstrap-logserver.sh"
  end # of log_config

  # create File Server
  config.vm.define "file" do |file_config|
    file_config.vm.box = "ubuntu/bionic64"
    file_config.vm.hostname = "file"
    file_config.vm.network "private_network", ip: "192.168.57.11"
    file_config.vm.provider "virtualbox" do |vb|
        vb.name = "file"
        vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
        vb.memory = "512"
        vb.customize ["modifyvm", :id, "--uart1", "0x3F8", "4"]
        vb.customize ["modifyvm", :id, "--uartmode1", "file", File::NULL]
    end # of vb
    # Shared folders
    if Vagrant::Util::Platform.windows? then
      # Configuration SPECIFIC for Windows 10 hosts
      file_config.vm.synced_folder "fileserver", "/var/repo/fileserver",
      id: "vagrant-root", owner: "www-data", group: "www-data",
      mount_options: ["dmode=775", "fmode=775"]
    else
      # Configuration for Unix/Linux hosts
      file_config.vm.synced_folder "fileserver", "/var/repo/fileserver",
      owner: "www-data", group: "www-data",
      mount_options: ["dmode=775", "fmode=775"]
    end # of shared folders
    # Provisioning
    file_config.vm.provision "shell", path: "provisioning/bootstrap-fileserver.sh"
  end # of file_config

  config.vm.define "bs1" do |bs1_config|
    # Every Vagrant development environment requires a box.
    bs1_config.vm.box = "ubuntu/bionic64"
    # Assign a friendly name to this host VM
    bs1_config.vm.hostname = "bs1"
    # Create a private network, which allows host-only access to the machine
    bs1_config.vm.network "private_network", ip: "192.168.58.11"
    # Provider-specific configuration so you can fine-tune various
    bs1_config.vm.provider "virtualbox" do |vb|
        # Change the VM name/ID in the Hypervisor
        vb.name = "bs1"
        vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
        vb.memory = "512"
        vb.customize ["modifyvm", :id, "--uart1", "0x3F8", "4"]
        vb.customize ["modifyvm", :id, "--uartmode1", "file", File::NULL]
    end # of vb
    # Shared folders
        if Vagrant::Util::Platform.windows? then
          # Configuration SPECIFIC for Windows 10 hosts
          bs1_config.vm.synced_folder "backupserver1", "/var/repo/backupserver",
          id: "vagrant-root", owner: "www-data", group: "www-data",
          mount_options: ["dmode=775", "fmode=775"]
        else
          # Configuration for Unix/Linux hosts
          bs1_config.vm.synced_folder "backupserver1", "/var/repo/backupserver",
          owner: "www-data", group: "www-data",
          mount_options: ["dmode=775", "fmode=775"]
    end # of shared folders
    # Provisioning
    bs1_config.vm.provision "shell", path: "provisioning/bootstrap-backups.sh"
  end # of  bs_config

   config.vm.define "bs2" do |bs2_config|
      # Every Vagrant development environment requires a box.
      bs2_config.vm.box = "ubuntu/bionic64"
      # Assign a friendly name to this host VM
      bs2_config.vm.hostname = "bs2"
      # Create a private network, which allows host-only access to the machine
      bs2_config.vm.network "private_network", ip: "192.168.58.12"
      # Provider-specific configuration so you can fine-tune various
      bs2_config.vm.provider "virtualbox" do |vb|
          # Change the VM name/ID in the Hypervisor
          vb.name = "bs2"
          vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
          vb.memory = "512"
          vb.customize ["modifyvm", :id, "--uart1", "0x3F8", "4"]
          vb.customize ["modifyvm", :id, "--uartmode1", "file", File::NULL]
      end # of vb
      # Shared folders
          if Vagrant::Util::Platform.windows? then
            # Configuration SPECIFIC for Windows 10 hosts
            bs2_config.vm.synced_folder "backupserver2", "/var/repo/backupserver",
            id: "vagrant-root", owner: "www-data", group: "www-data",
            mount_options: ["dmode=775", "fmode=775"]
          else
            # Configuration for Unix/Linux hosts
            bs2_config.vm.synced_folder "backupserver2", "/var/repo/backupserver",
            owner: "www-data", group: "www-data",
            mount_options: ["dmode=775", "fmode=775"]
      end # of shared folders
      # Provisioning
      bs2_config.vm.provision "shell", path: "provisioning/bootstrap-backups.sh"
    end # of  bs_config

  # Create an new instance
  # insert your instructions here:
  (1..2).each do |i|
    config.vm.define "client#{i}" do |client_config|
        # Every Vagrant development environment requires a box.
        client_config.vm.box = "ubuntu/bionic64"
        # Assign a friendly name to this host VM
        client_config.vm.hostname = "client#{i}"
        # Create a private network, which allows host-only access to the machine
        client_config.vm.network "private_network", ip: "192.168.59.1#{i}"
        # Provider-specific configuration so you can fine-tune various
        client_config.vm.provider "virtualbox" do |vb|
            # Change the VM name/ID in the Hypervisor
            vb.name = "client#{i}"
            vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
            vb.memory = "256"
            vb.customize ["modifyvm", :id, "--uart1", "0x3F8", "4"]
            vb.customize ["modifyvm", :id, "--uartmode1", "file", File::NULL]
        end # of vb
        # Shared folders
        if Vagrant::Util::Platform.windows? then
          # Configuration SPECIFIC for Windows 10 hosts
          client_config.vm.synced_folder "client", "/home/vagrant/client",
          id: "vagrant-root", owner: "vagrant", group: "vagrant",
          mount_options: ["dmode=775", "fmode=775"]
        else
          # Configuration for Unix/Linux hosts
          client_config.vm.synced_folder "client", "/home/vagrant/client",
          mount_options: ["dmode=775", "fmode=775"]
        end # of shared folders
    # Provisioning
    client_config.vm.provision "shell", path: "provisioning/bootstrap-client.sh"
    end # of client_config
  end # end of loop
end # of config
