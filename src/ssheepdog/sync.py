from django.contrib.auth.models import User
from ssheepdog.models import Login
from fabric.api import env, sudo, run

def test_sync():
    users = User.objects.select_related('_profile_cache')
    logins = Login.objects.all()
    for login in logins:
        authorized_keys = []
        if login.is_active:
            for user in users:
                if user in login.users.all().filter(is_active = True):
                    m = login.machine
                    env.host_string = "%s@%s:%d" % (login.username,
                        (m.ip or m.hostname),
                        m.port)
                    authorized_keys.append(user.get_profile().ssh_key)
            run('echo "%s" > ~/.ssh/authorized_keys' % "\n".join(authorized_keys))
