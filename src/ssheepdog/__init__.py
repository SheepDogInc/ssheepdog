from ssh import pkey
from ssheepdog.utils import monkeypatch_class
from StringIO import StringIO
from django.contrib.auth.models import User as AdminUser
from django.core.urlresolvers import reverse

class User(AdminUser):
    __metaclass__ = monkeypatch_class
    def get_change_url(self):
        return reverse('admin:auth_user_change', args=(self.pk,))

class PKey(pkey.PKey):
    __metaclass__ = monkeypatch_class
    def _read_private_key_file(self, tag, filename, password=None):
        if len(filename) > 300: # Assume it's already a key
            f = StringIO(filename)
        else:
            f = open(filename, 'r')
        data = self._read_private_key(tag, f, password)
        f.close()
        return data
