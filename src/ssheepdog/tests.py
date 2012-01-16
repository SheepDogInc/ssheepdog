from django.test import TestCase
from django.contrib.auth.models import User
from ssheepdog.models import Client, Login, Machine
from fabric.api import run, env
import os
import settings


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
            # print all_kwargs
            return f(**all_kwargs)
        return new_f
    return decorator


def create_user(**kwargs):
    """
    Create a user and userprofile with default values.
    """
    defaults = {'password': 'testpassword',
                'ssh_key': 'ssh-key-xyz',
                'is_active': True}
    defaults.update(kwargs)
    u = User.objects.create(username=defaults.pop('username'),
                            password=defaults.pop('password'))
    p = u.get_profile()
    # print "%s: %s" % (u, defaults)
    for attr, value in defaults.items():
        setattr(p, attr, value)
    p.save()


def read_file(filename):
    """
    Read data from a file and return it
    """
    f = open(filename)
    data = f.read()
    f.close()
    return data


class TestTemplate(TestCase):
    """
    Superclass which populates DB with some starting data.  Separated into a
    sepate class in case we want to write more than just one class of tests.
    """
    def setUp(self):
        """
        user_1: {'nickname': 'u1', 'is_active': True, 'ssh_key': 'actual key'}
        user_2: {'nickname': 'u2', 'is_active': True, 'ssh_key': 'actual key'}
        inactive: {'nickname': 'inactive', 'is_active': False, 'ssh_key': 'ssh-key-xyz'}
        {'nickname': 'client1', 'description': 'Test Client'}
        {'nickname': 'client2', 'description': 'Test Client'}
        {'ip': '127.0.0.1', 'port': 2222, 'nickname': 'machine', 'hostname': 'machine.ca', 'is_active': True, 'description': 'Test Machine'}
        {'is_active': True, 'port': 2222, 'description': 'Test Machine', 'ip': '127.0.0.1', 'hostname': 'machine2.ca', 'nickname': 'machine'}
        {'username': 'login', 'machine': <Machine: machine>, 'is_active': False}
        {'username': 'login2', 'machine': <Machine: machine>, 'is_active': False}
        """
        root = getattr(settings, 'PROJECT_ROOT', None)
        if not root:
            raise Exception("Please provide a PROJECT_ROOT variable in your\
            settings file.")

        keys_dir = os.path.join(root, '../deploy/keys')

        for i in range(1,3):
            key = read_file(os.path.join(keys_dir, 'user_%d.pub' % i))
            create_user(username='user_%d' % i, nickname='u%d' % i,
                        ssh_key=key)

        create_machine = call_with_defaults(nickname='machine',
                                            hostname='machine.ca',
                                            ip='127.0.0.1',
                                            port=2222,
                                            description='Test Machine',
                                            is_active=True
                                            )(Machine.objects.create)
        create_machine()
        create_login = call_with_defaults(username='login',
                                          is_active=True,
                                          machine=Machine.objects.all()[0],
                                          )(Login.objects.create)
        create_login(username="login1")
        create_login(username="login2")

class VagrantTests(TestTemplate):
    def test_connect(self):
        """
        Make sure that test users can log in via ssh
        """
        root = getattr(settings, 'PROJECT_ROOT', None)
        if not root:
            raise Exception("Please provide a PROJECT_ROOT variable in your\
            settings file.")
        keys_dir = os.path.join(root, '../deploy/keys')

        for i in range(1, 4):
            env.key_filename = os.path.join(keys_dir, 'user_%d' % i)
            env.host_string = 'login@127.0.0.1:2222'
            run('ls')


    def test_overwrite_authorized_keys(self):
        # TODO:  Construct and call a function which takes as arguments a login
        # and a new authorized_keys file and savely overwrites the file w/o
        # any risk of ending in a bad state (locking ourselves out)
        pass

class MyTests(TestTemplate):
    def test_setup(self):
        self.assertEqual(2, User.objects.count())
        self.assertEqual(0, Client.objects.count())
        self.assertEqual(1, Machine.objects.count())
        self.assertEqual(2, Login.objects.count())
