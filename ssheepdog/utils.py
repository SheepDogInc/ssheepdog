from django.core.exceptions import ObjectDoesNotExist
from StringIO import StringIO
import sys

def read_file(filename):
    """
    Read data from a file and return it
    """
    f = open(filename)
    data = f.read()
    f.close()
    return data

def monkeypatch_class(name, bases, namespace):
    assert len(bases) == 1, "Exactly one base class required"
    base = bases[0]
    for name, value in namespace.iteritems():
        if name != "__metaclass__":
            setattr(base, name, value)
    return base

class DirtyFieldsMixin(object):
    """
    Supplies method get_dirty_fields() which is a dict of those fields which
    have changed since object creation, mapping field names to original values.

    A foreign key field is dirty if its pk changes; changes to the other object
    are not detected.  The dirty field is listed as fieldname_pk, and the
    original value is either the pk itself or None.

    Many-to-many fields are ignored.
    """
    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)
        self._original_state = self._as_dict()

    def _as_dict(self):
        def name(f):
            return "%s_pk" % f.name if f.rel else f.name

        def value(f):
            if f.rel: # Usually the primary key is the "_id"...
                try:
                    return getattr(self, f.name + "_id")
                except AttributeError:
                    pass

            try:
                val = getattr(self, f.name)
            except ObjectDoesNotExist: # foreign key relation not yet set
                val = None
            if f.rel and val:
                return val.pk
            else:
                return val
        return dict([(name(f), value(f)) for f in self._meta.local_fields])

    def get_dirty_fields(self):
        new_state = self._as_dict()
        return dict([(key, value)
                     for key, value in self._original_state.iteritems()
                     if value != new_state[key]])

def generate_new_application_key():
    from ssheepdog import models
    from django.db import transaction
    with transaction.commit_on_success():
        models.ApplicationKey.get_latest(create_new = True)
        models.Login.objects.update(is_dirty=True)

class capture_output(object):
    """
    Usage:
    with capture_output() as captured:
        do_stuff()
    Now captured.stderr and captured.stdout contain the output generated during
    do_stuff().  capture_output(stderr=False) turns the latter off.
    """

    backup = None
    result = None

    def __init__(self, stderr=True, stdout=True):
        self.capture_stdout = stdout
        self.capture_stderr = stderr

    def __enter__(self):
        class Result(object):
            stdout = ""
            stderr = ""
        self.result = Result()
        if self.capture_stderr:
            self.stderr = sys.stderr
            sys.stderr = StringIO()
        if self.capture_stdout:
            self.stdout = sys.stdout
            sys.stdout = StringIO()
        return self.result

    def __exit__(self, type, value, traceback):
        if self.capture_stderr:
            self.result.stderr = sys.stderr.getvalue()
            sys.stderr.close()
            sys.stderr = self.stderr
        if self.capture_stdout:
            self.result.stdout = sys.stdout.getvalue()
            sys.stdout.close()
            sys.stdout = self.stdout

def add_permission(orm, codename, name, app_label='ssheepdog', model='login'):
    ct, created = orm['contenttypes.ContentType'].objects.get_or_create(
        model=model, app_label=app_label)
    orm['auth.permission'].objects.get_or_create(
        content_type=ct, codename=codename, defaults=dict(name=name))
