Vagrant::Config.run do |config|
  config.vm.forward_port 22, 2222
  config.vm.customize ["modifyvm", :id, "--memory", "128"]

  config.vm.box = "sd-natty"

  config.vm.provision :chef_solo do |chef|
    chef.cookbooks_path = "deploy/cookbooks"
    chef.add_recipe "ssheepdog::default"
  end

end
