# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.customize ["modifyvm", :id, "--memory", "128"]
  config.vm.box = "ubuntu-12.04-x64"
  config.vm.network :hostonly, "127.0.0.1"
  config.vm.provision :chef_solo do |chef|
    chef.cookbooks_path = "deploy/cookbooks"
    chef.add_recipe "ssheepdog::default"
  end
end

# Vagrant::Config.run do |config|
#   config.vm.customize ["modifyvm", :id, "--memory", "128"]

#   config.vm.box = "ubuntu-12.04-x64"

#   config.vm.provision :chef_solo do |chef|
#     chef.cookbooks_path = "deploy/cookbooks"
#     chef.add_recipe "ssheepdog::default"
#   end

# end

