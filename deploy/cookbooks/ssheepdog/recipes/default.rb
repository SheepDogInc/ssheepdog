group "ssheepdog" do
    gid 1337
end

user "ssheepdog" do
    username "ssheepdog"
    comment "Application User"
    gid 1337
    uid 1337
    shell "/bin/bash"
    home "/home/ssheepdog"
end

group "sudoers" do
    members ['ssheepdog']
end

directory "/home/ssheepdog" do
    owner "ssheepdog"
    group "ssheepdog"
    mode 0755
end

directory "/home/ssheepdog/.ssh" do
    owner "ssheepdog"
    group "ssheepdog"
    mode 0700
end

cookbook_file "/home/ssheepdog/.ssh/authorized_keys" do
    source "authorized_keys"
    owner "ssheepdog"
    group "ssheepdog"
    mode 0600
end

script "Add ssheepdog user to sodoers" do
    interpreter "bash"
    code <<-EOH
    if grep --quiet 'sudoers ALL=NOPASSWD:ALL' ; then
        echo "User already in sudoers"
    else
        cp /etc/sudoers /etc/sudoers.orig
        echo "%sudoers ALL=NOPASSWD:ALL" >> /etc/sudoers
    fi
    EOH
end


group "logingroup" do
    gid 1339
end

user "login" do
    username "login"
    comment "Application User"
    gid 1339
    uid 1339
    shell "/bin/bash"
    home "/home/login"
end

group "sudoers" do
    members ['login']
end

directory "/home/login" do
    owner "login"
    group "logingroup"
    mode 0755
end

directory "/home/login/.ssh" do
    owner "login"
    group "logingroup"
    mode 0700
end

cookbook_file "/home/login/.ssh/authorized_keys" do
    source "authorized_keys"
    owner "login"
    group "logingroup"
    mode 0600
end

script "Add login user to sodoers" do
    interpreter "bash"
    code <<-EOH
    if grep --quiet 'sudoers ALL=NOPASSWD:ALL' ; then
        echo "User already in sudoers"
    else
        cp /etc/sudoers /etc/sudoers.orig
        echo "%sudoers ALL=NOPASSWD:ALL" >> /etc/sudoers
    fi
    EOH
end
