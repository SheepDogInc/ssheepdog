Installation
============

Ssheepdog doesn't yet come as a reusable Django app, so we have provided a
starter Django project for you.

::

    $ git clone git://github.com/SheepDogInc/ssheepdog.git
    $ cd ssheepdog
    $ pip install -r requirements.txt
    $ cd src
    $ python manage.py syncdb
    $ python manage.py migrate
    $ python manage.py runserver

And the application will be running on ``http://localhost:8000``.

.. note:: We **strongly** recommend using `virtualenv`_ when installing
    ssheepdog.

.. _virtualenv: http://www.virtualenv.org/en/latest/index.html
