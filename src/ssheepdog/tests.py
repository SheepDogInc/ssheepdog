from django.test import TestCase
from django.contrib.auth.models import User
from ssheepdog.models import Client, Login, Machine
from fabric.api import run, env
import os
import settings
import fabric.utils
root = getattr(settings, 'PROJECT_ROOT', None)
if not root:
    raise Exception("Please provide a PROJECT_ROOT variable in your"
                    " settings file.")
keys_dir = os.path.join(root, '../deploy/keys')
from sync import test_sync

def read_file(filename):
    """
    Read data from a file and return it
    """
    f = open(filename)
    data = f.read()
    f.close()
    return data

def flag_test(flag):
    """
    Decorator to flag a test and restrict whether it is run according to
    settings.SKIP_TESTS_WITH_FLAGS
    """
    def decorator(f):
        def new_f(*args, **kwargs):
            if flag in getattr(settings, 'SKIP_TESTS_WITH_FLAGS', []):
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
        defaults['ssh_key'] = read_file(os.path.join(keys_dir, kwargs['username']+".pub"))
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

    def test_connect(self):
        """
        Make sure that test users can log in via ssh
        """
        for i in range(1, 4):
            env.key_filename = os.path.join(keys_dir, 'user_%d' % i)
            env.host_string = 'login@127.0.0.1:2222'
            run('ls')

def can_connect(user, login):
    """
    Try to connect to the given login using the credential of user
    """
    m = login.machine
    env.abort_on_prompts = True
    env.key_filename = os.path.join(keys_dir, user.username)
    env.host_string = "%s@%s:%s" % (login.username,
                                    m.ip or m.hostname,
                                    m.port)
    try:
        run('echo')
        return True
    except SystemExit:
        return False

class PushKeyTests(TestCase):
    def setUp(self):
        self.user = create_user(username='user_1')
        self.machine = create_machine()
        self.login = create_login(username="login", machine=self.machine)

    def test_cannot_connect(self):
        test_sync()
        self.assertFalse(can_connect(self.user, self.login))

    def test_key_push(self):
        self.login.users = [self.user]
        self.login.save()
        test_sync()
        self.assertTrue(can_connect(self.user, self.login))
