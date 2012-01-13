from django.contrib.auth.models import User
from ssheepdog.models import Login
from fabric.api import env, sudo, run

def test_sync():
    users = User.objects.select_related('_profile_cache')
    logins = Login.objects.all()
    authorized_keys = []
    for user in users:
        user.ssh_key = user.get_profile().ssh_key
    for login in logins:
        for user in users:
            if user in login.users.all():
                m = login.machine
                env.host_string = "%s@%s:%d" % (login.username,
                        (m.ip or m.hostname),
                        m.port)
                authorized_keys.append(str(user.ssh_key))
        print str(env.host_string)
        run('echo "%s" > ~/.ssh/authorized_keys' % "\n".join(authorized_keys))
