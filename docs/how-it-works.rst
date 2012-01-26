How it works
============

This section will give you an overview of how ssheepdog works. You should
understand this model before you use this application in a production
environment.

Models
------

There are three main models:

* User
* Machine
* Login

The User model represents a member of your team. It's a real person who can log
into the application. This uses the built-in Django User model along with a
custom ``UserProfile`` class. The User has the ability to access and edit their
own account. They are required to specify their public ssh key once their
account is created.

The Machine model represents a server. A Machine will typically have an IP
address or a hostname. You can specify a client for each machine, if it's
active, etc.

Each Machine will have one or more Logins associated with it. A Login is the
unix username that you log in as on the Machine. Each Login knows what Users
can log in with that account.


Administration
--------------

Once the application is deployed, you will be able to specify which physical
Users can log into what Machines via what Logins. Once your changes are made,
you will start the syncing process.

Syncing
-------

The basic idea behind synchronization is to update the ``authorized_keys`` file
for each login on the remote server. This file is based on the list of
authorized Users for a given Login. Furthermore, the ssheepdog application
itself uses an ssh key pair to log into each machine. The application's ssh key
is renewed each time a sync is run.
