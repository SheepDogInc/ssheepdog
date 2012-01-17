from ssheepdog.models import Login
from fabric.api import env, run
import os
from tests import keys_dir

def read_file(filename):
    """
    Read data from a file and return it
    """
    f = open(filename)
    data = f.read()
    f.close()
    return data

def test_sync():
    for login in Login.objects.all():
        authorized_keys = [read_file(os.path.join(keys_dir, 'application.pub'))]
        m = login.machine
        env.abort_on_prompts = True
        env.key_filename = os.path.join(keys_dir, 'application')
        env.host_string = "%s@%s:%d" % (login.username,
                (m.ip or m.hostname),
                m.port)    
        if login.is_active and login.machine.is_active:
            for user in (login.users
                         .filter(is_active = True)
                         .select_related('_profile_cache')):
                authorized_keys.append(user.get_profile().ssh_key)
        run('echo "%s" > ~/.ssh/authorized_keys' % "\n".join(authorized_keys))
