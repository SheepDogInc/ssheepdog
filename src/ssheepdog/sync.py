from django.contrib.auth.models import User
from django.template import Context, loader
from src import ssheepdog
from ssheepdog.models import UserProfile, Machine, Login, Client


class Sync(object):
    def __init__(self, path=None):
        users = User.objects.select_related('_profile_cache')
        logins = login.objects.all()
        authorized_keys = []
        for user in users:
            user.ssh_key = user.get_profile().ssh_key
        for login in logins:
            for user in users:
                if user in login.users.all():
                    env.host_string = login.username+"@"+login.machine     
                    authorized_keys.append(user.ssh_key)
        sudo('echo "%s" > ~/.ssh/authorized_keys' %
            authorized_keys)
