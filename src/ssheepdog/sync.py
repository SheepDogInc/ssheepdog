from django.contrib.auth.models import User
from ssheepdog.models import Login
from fabric.api import env, sudo

def test_sync():
    users = User.objects.select_related('_profile_cache')
    logins = Login.objects.all()
    authorized_keys = []
    for user in users:
        user.ssh_key = user.get_profile().ssh_key
    for login in logins:
        for user in users:
            if user in login.users.all():
                env.host_string = login.username+"@" + str(login.machine)
                authorized_keys.append(str(user.ssh_key))
        sudo ('echo "%s" > ~/.ssh/authorized_keys_test' % "\n".join(authorized_keys))
