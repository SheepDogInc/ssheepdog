"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from ssheepdog.models import Client, Login, Machine
import settings

def slow_test(f):
    """
    Decorator to flag a test as slow.  Skip if settings.SKIP_SLOW_TESTS
    if set to True
    """
    def new_f(*args, **kwargs):
        if getattr(settings, 'SKIP_SLOW_TESTS', False):
            return None
        else:
            return f(*args, **kwargs)
    return new_f

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

class TestTemplate(TestCase):
    """
    Superclass which populates DB with some starting data.  Separated into a
    sepate class in case we want to write more than just one class of tests.
    """
    def setUp(self):
        """
        user_1: {'nickname': 'u1', 'is_active': True, 'ssh_key': 'ssh-key-xyz-1'}
        user_2: {'nickname': 'u2', 'is_active': True, 'ssh_key': 'ssh-key-xyz-2'}
        user_3: {'nickname': 'u3', 'is_active': True, 'ssh_key': 'ssh-key-xyz-3'}
        inactive: {'nickname': 'inactive', 'is_active': False, 'ssh_key': 'ssh-key-xyz'}
        {'nickname': 'client1', 'description': 'Test Client'}
        {'nickname': 'client2', 'description': 'Test Client'}
        {'ip': '12.34.56.78', 'nickname': 'machine', 'hostname': 'machine.ca', 'is_active': True, 'description': 'Test Machine'}
        {'is_active': True, 'description': 'Test Machine', 'ip': '12.34.56.78', 'hostname': 'machine2.ca', 'nickname': 'machine'}
        {'username': 'login', 'machine': <Machine: machine>, 'is_active': False}
        {'username': 'login2', 'machine': <Machine: machine>, 'is_active': False}
        """

        for i in range(1,4):
            create_user(username='user_%d' % i, nickname='u%d' % i,
                        ssh_key="ssh-key-xyz-%d" % i)
        create_user(username='inactive', nickname='inactive', is_active=False)
        create_client = call_with_defaults(nickname='client',
                                           description='Test Client'
                                           )(Client.objects.create)
        create_client(nickname='client1')
        create_client(nickname='client2')
        create_machine = call_with_defaults(nickname='machine',
                                            hostname='machine.ca',
                                            ip='12.34.56.78',
                                            description='Test Machine',
                                            is_active=True
                                            )(Machine.objects.create)
        create_machine()
        create_machine(hostname='machine2.ca', is_active=True)
        create_login = call_with_defaults(username='login',
                                          is_active=False,
                                          machine=Machine.objects.all()[0],
                                          )(Login.objects.create)
        create_login()
        create_login(username="login2", is_active=False)


class MyTests(TestTemplate):
    def test_setup(self):
        self.assertEqual(4, User.objects.count())
        self.assertEqual(2, Client.objects.count())
        self.assertEqual(2, Machine.objects.count())
        self.assertEqual(2, Login.objects.count())
