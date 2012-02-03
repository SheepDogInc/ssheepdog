Developing
==========

django-ssheepdog is distributed as a pluggable django app. The meat of the
application is contained in the ``ssheepdog`` directory. The ``src`` directory
contains a django project that uses the app.

When you are developing, you should install ssheepdog into your virtual
environment with the following command:

::

    $ python setup.py develop

This will create a symlink between the source and the environment's site
packages. Once the link is created, you can edit the source code in
``ssheepdog/`` as usual.

Vagrant
-------

We have provided a vagrant VM configuration for testing the ssh syncing.

Boot it up:

::

    $ vagrant up

Log in:

::

    $ ssh ssheepdog@127.0.0.1 -p 2222 -i deploy/cookbooks/ssheepdog/files/default/id_rsa
