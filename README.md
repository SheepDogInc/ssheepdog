ssheepdog
=========

ssheepdog is a public ssh key management tool for teams of programmers.
Different people need different privileges to different servers. Ssheepdog
allows you to specify these relationships and then sync the keys to the
appropriate servers.

**Note**: This is very much alpha software.

`ssheepdog` is a django app and it's contained in the `src/` directory. You
should be able to run it locally without much trouble.

Testing vagrant VM
------------------
We have provided a vagrant VM configuration for testing the ssh syncing.

Boot it up:

    $ vagrant up

Log in:

    $ ssh ssheepdog@127.0.0.1 -p 2222 -i deploy/cookbooks/ssheepdog/files/default/id_rsa
