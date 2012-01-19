from django.test import TestCase
from django.contrib.auth.models import User
from ssheepdog.models import Client, Login, Machine, FABRIC_WARNINGS
import os
import settings as app_settings
from fabric.network import disconnect_all
from ssheepdog.models import KEYS_DIR
from sync import test_sync
from utils import read_file
from fabric.api import run, env, hide, settings

def flag_test(flag):
    """
    Decorator to flag a test and restrict whether it is run according to
    settings.SKIP_TESTS_WITH_FLAGS
    """
    def decorator(f):
        def new_f(*args, **kwargs):
            if flag in getattr(app_settings, 'SKIP_TESTS_WITH_FLAGS', []):
                return None
            else:
                return f(*args, **kwargs)
        return new_f
    return decorator


def call_with_defaults(**defaults):
    def decorator(f):
        def new_f(**kwargs):
            all_kwargs = {}
            all_kwargs.update(defaults)
            all_kwargs.update(kwargs)
            return f(**all_kwargs)
        return new_f
    return decorator

def create_user(**kwargs):
    """
    Create a user and userprofile with default values.
    """

    defaults = {'password': 'testpassword',
                'is_active': True}
    if not kwargs.get('ssh_key') and kwargs.get('username'):
        u = kwargs['username']
        defaults['ssh_key'] = read_file(os.path.join(KEYS_DIR, kwargs['username']+".pub"))
    defaults['nickname'] = kwargs['username']
    defaults.update(kwargs)
    username = defaults.pop('username')
    u = User.objects.create(username=username,
                            password=defaults.pop('password'))
    p = u.get_profile()
    for attr, value in defaults.items():
        setattr(p, attr, value)
    p.save()
    return u

create_machine = call_with_defaults(nickname='machine',
                                    hostname='machine.ca',
                                    ip='127.0.0.1',
                                    port=2222,
                                    description='Test Machine',
                                    is_active=True
                                    )(Machine.objects.create)

create_login = call_with_defaults(username='login',
                                  is_active=True,
                                  )(Login.objects.create)


class VagrantTests(TestCase):
    def setUp(self):
        create_user(username='user_1')
        create_user(username='user_2')

        m = create_machine()
        create_login(username="login1", machine=m)
        create_login(username="login2", machine=m)

    def test_setup(self):
        self.assertEqual(2, User.objects.count())
        self.assertEqual(0, Client.objects.count())
        self.assertEqual(1, Machine.objects.count())
        self.assertEqual(2, Login.objects.count())

    @flag_test('requires_server')
    def test_connect(self):
        """
        Make sure that test users can log in via ssh
        """
        for i in range(1, 4):
            env.key_filename = os.path.join(KEYS_DIR, 'user_%d' % i)
            env.host_string = 'login@127.0.0.1:2222'
            run('ls')

def can_connect(user, login):
    """
    Try to connect to the given login using the credential of user
    """
    return login.run('echo', private_key_filename=user.username)

def key_present(user,login):
    return user.get_profile().ssh_key in login.get_authorized_keys()

def sync():
    with settings(hide(*FABRIC_WARNINGS)):
        test_sync()
        disconnect_all()

class PushKeyTests(TestCase):
    def setUp(self):
        self.user = create_user(username='user_1')
        self.user2 = create_user(username='user_2')
        self.machine = create_machine()
        self.login = create_login(username="login", machine=self.machine)

    #@flag_test('requires_server')
    def test_user_login_disconnected(self):
        sync()
        self.assertFalse(key_present(self.user, self.login))

    @flag_test('requires_server')
    def test_key_push(self):
        self.login.users = [self.user]
        self.login.save()
        sync()
        self.assertTrue(can_connect(self.user, self.login))

    @flag_test('requires_server')
    def test_machine_inactive(self):
        self.login.users = [self.user]
        self.machine.is_active = False
        self.machine.save()
        self.login.save()
        sync()
        self.assertFalse(can_connect(self.user, self.login))

    def test_machine_login_inactive_user_active(self):
        self.login.users = [self.user] 
        self.machine.is_active = False
        self.login.is_active = False
        self.machine.save()
        self.login.save()
        self.assertFalse(key_present(self.user, self.login))

    def test_two_users(self):
        self.login.users = [self.user, self.user2] 
        self.login.save()
        self.assertTrue(key_present(self.user, self.login))
        self.assertTrue(key_present(self.user2, self.login))

    def test_bad_machine(self):
        self.login.users = [self.user]
        self.machine.port = 10
        self.machine.save()
        self.login.save()
        self.assertFalse(can_connect(self.user,self.login))

class DirtyTests(TestCase):
    def setUp(self):
        self.user = create_user(username='user_1')
        self.user2 = create_user(username='user_2')
        self.machine = create_machine()
        self.login = create_login(username="login", machine=self.machine)
        self.login.is_dirty = False
        self.login.save()
    
    def assertDirty(self):
        login = Login.objects.get()
        self.assertTrue(login.is_dirty)

    def assertClean(self):
        login = Login.objects.get()
        self.assertFalse(login.is_dirty)

    def test_dirty(self):
        Login.objects.all().delete()
        create_login(username="login", machine=self.machine)
        self.assertDirty()

    def test_clean(self):
        self.assertClean()

    def test_client(self):
        """Changing the client should not dirty the login"""
        self.login.client = Client.objects.create(nickname="joe")
        self.login.save()
        self.assertClean()

    def test_username(self):
        """Changing the username requires pushing out new keys... dirty"""
        self.login.username = "changed"
        self.login.save()
        self.assertDirty()

    def test_user(self):
        """Changing the m2m for a user makes the login dirty"""
        self.login.users = []
        self.login.save()

    def test_machine(self):
        """Changing the machine should make all the logins associated dirty"""
        self.machine.is_active = False
        self.machine.save()
        self.assertDirty()

    def test_machine_not_dirty(self):
        """Tests that the logins connected to the machine does not get dirtyed
        when an unimportant machine field is changed"""
        self.machine.nickname = False
        self.machine.save()
        self.assertClean()
