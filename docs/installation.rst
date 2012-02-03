Installation
============

* Install django-ssheepdog with pip ::

    $ pip install -e git+git://github.com/sheepdoginc/django-ssheepdog.git@dev#egg=django-ssheepdog

* Add ``ssheepdog`` to your ``INSTALLED_APPS`` setting ::

    INSTALLED_APPS = (
        # other apps
        'ssheepdog',
    )

* Add django-ssheepdog urls to your project's ``urls.py`` ::

    urlpatterns = patterns('',
        url('^ssheepdog/', include('ssheepdog.urls')),
    )

* Sync and migrate your database


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
