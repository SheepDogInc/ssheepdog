django-ssheepdog
================

django-ssheepdog is a public ssh key management tool for teams of programmers.
Different people need different privileges to different servers. Ssheepdog
allows you to specify these relationships and then sync the keys to the
appropriate servers.

**Note**: This is very much alpha software.

Development
-----------

django-ssheepdog is distributed as a pluggable django app. The meat of the
application is contained in the `ssheepdog` directory. The `src` directory
contains a django project that uses the app.

When you are developing, you should install ssheepdog into your virtual
environment with the following command:

    $ python setup.py develop

This will create a symlink between the source and the environment's site
packages. Once the link is created, you can edit the source code in
`ssheepdog/` as usual.

Installation
------------

To install the latest version, run:

    $ pip install -e git+git://github.com/sheepdoginc/django-ssheepdog.git@dev#egg=django-ssheepdog

Then, add `ssheepdog` to your `INSTALLED_APPS` and add the `ssheepdog.urls` to
your project's urls.

The project isn't on PyPI yet.

Documentation
-------------
Latest documentation can be found on [ReadTheDocs][1].

Testing vagrant VM
------------------
We have provided a vagrant VM configuration for testing the ssh syncing.

Boot it up:

    $ vagrant up

Log in:

    $ ssh ssheepdog@127.0.0.1 -p 2222 -i deploy/cookbooks/ssheepdog/files/default/id_rsa


[1]: http://ssheepdog.readthedocs.org/en/latest/index.html
