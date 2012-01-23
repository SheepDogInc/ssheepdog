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

Celery tasks
------------

If you have a lot of servers to sync, you may wish to run the sync process in
the background. This is the recommended setup for production use since a real
web server will timeout with such a long running request. There is a celery
task that you can use to accomplish this.

In addition to your development server, you will need to run a celery worker.

::

    $ python manage.py celeryd -l info

Then, you can run a background task like this:

.. code-block:: python

    from ssheepdog.tasks import sync

    sync.delay()


.. _virtualenv: http://www.virtualenv.org/en/latest/index.html
