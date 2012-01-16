from django.contrib.auth.models import User
from ssheepdog.models import Login
from fabric.api import env, sudo, run
import os
import settings

root = getattr(settings, 'PROJECT_ROOT', None)
keys_dir = os.path.join(root, '../deploy/keys')
def test_sync():
    users = User.objects.select_related('_profile_cache')
    logins = Login.objects.all()
    for login in logins:
        authorized_keys = []
        env.key_filename = os.path.join(keys_dir, 'application')
        authorized_keys.append(read_file(os.path.join(keys_dir,'application.pub')))
        if login.is_active:
            for user in users:
                if user in login.users.all().filter(is_active = True):
                    m = login.machine
                    env.host_string = "%s@%s:%d" % (login.username,
                        (m.ip or m.hostname),
                        m.port)
                    authorized_keys.append(user.get_profile().ssh_key)
            run('echo "%s" > ~/.ssh/authorized_keys_test' % "\n".join(authorized_keys))
def read_file(filename):
       """
       Read data from a file and return it
       """
       f = open(filename)
       data = f.read()
       f.close()
       return data
