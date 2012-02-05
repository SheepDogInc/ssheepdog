from ssh import pkey
from ssheepdog.utils import monkeypatch_class
from StringIO import StringIO
from django.contrib.auth.models import User as AdminUser
from django.core.urlresolvers import reverse

class User(AdminUser):
    __metaclass__ = monkeypatch_class
    def get_change_url(self):
        return reverse('admin:auth_user_change', args=(self.pk,))

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self._was_active = self.is_active

    def get_nickname(self):
        try:
            return self.get_profile().nickname or self.email
        except AttributeError:
             # A User created through management has no profile
             # Create one!
            from ssheepdog.models import UserProfile
            UserProfile.objects.create(user=self)
            return User.objects.get(pk=self.pk).get_profile().nickname or self.email

    def save(self, *args, **kwargs):
        """
        If is_active was changed, then associated Logins need to be flagged as is_dirty
        """
        if self.pk and (self._was_active != self.is_active):
            from models import Login
            Login.objects.filter(users=self).update(is_dirty=True)
        super(User, self).save(*args, **kwargs)


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
