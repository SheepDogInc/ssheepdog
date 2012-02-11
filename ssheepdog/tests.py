from django.test import TestCase
from django.contrib.auth.models import User
from ssheepdog.models import Client, Login, Machine, ApplicationKey
from ssheepdog.fields import PublicKeyField
from ssheepdog.views import view_access_summary
import os
import settings as app_settings
from fabric.network import disconnect_all
from ssheepdog.models import KEYS_DIR
from utils import read_file
from fabric.api import run, env, hide, settings, local
from django.core import exceptions
from django.http import HttpRequest

def populate_ssheepdog_key():
    pub = read_file(os.path.join(KEYS_DIR, "ssheepdog.pub"))
    priv = read_file(os.path.join(KEYS_DIR, "ssheepdog"))
    ApplicationKey.objects.create(public_key=pub,
                                  private_key=priv)

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
    u = User.objects.create(username=defaults.pop('username'),
                            password=defaults.pop('password'))
    p = u.get_profile()
    for attr, value in defaults.items():
        setattr(p, attr, value)
        setattr(u, attr, value)
    p.save()
    u.save()
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

create_application_key = call_with_defaults(public_key = 'testpubkey',private_key ='testprikey')(ApplicationKey.objects.create)

class VagrantTests(TestCase):
    def setUp(self):
        populate_ssheepdog_key()
        self.user = create_user(username='user_1')
        self.machine = create_machine()
        self.login = create_login(username="login", machine=self.machine)
        self.reset_vagrant()

    @flag_test('requires_server')
    def reset_vagrant(self):
        with settings(hide('everything', 'status')):
            env.key_filename = local('vagrant ssh-config | grep IdentityFile',
                                     capture=True).split()[1]
            env.host_string = 'vagrant@127.0.0.1:2222'
            for u in ['login']:
                run('sudo bash -c "echo %s > ~%s/.ssh/authorized_keys"' % (
                    read_file(os.path.join(KEYS_DIR, "ssheepdog.pub")).strip(), u))
                run('sudo chown %s:logingroup ~%s/.ssh/authorized_keys' % (u,u))
            disconnect_all()
        env.key_filename = None

    @flag_test('requires_server')
    def test_connect(self):
        """
        Make sure that application can connect
        """
        env.key_filename = os.path.join(KEYS_DIR, 'ssheepdog')
        env.host_string = 'login@127.0.0.1:2222'
        with hide('everything'):
            run('ls')

    @flag_test('requires_server')
    def test_can_connect(self):
        """
        If user's key is injected, that user can now connect
        """
        self.login.users = [self.user]
        self.login.save()
        sync_all()
        self.assertTrue(can_connect(self.user, self.login))

    @flag_test('requires_server')
    def test_cannot_connect(self):
        self.login.users = []
        self.login.save()
        sync_all()
        self.assertFalse(can_connect(self.user, self.login))

    @flag_test('requires_server')
    def test_can_deploy_new_keys(self):
        latest = ApplicationKey.get_latest()
        self.assertEqual(self.login.get_application_key().pk,
                         latest.pk)
        latest = ApplicationKey.get_latest(create_new=True)
        self.assertNotEqual(self.login.get_application_key().pk,
                            latest.pk)
        sync_all()
        self.login = Login.objects.get(pk=self.login.pk)
        self.assertEqual(self.login.get_application_key().pk,
                         latest.pk)
        self.assertTrue(self.login.run('echo')) # Can still connect
        populate_ssheepdog_key()

def can_connect(user, login):
    """
    Try to connect to the given login using the credential of user
    """
    private_key = read_file(os.path.join(KEYS_DIR, user.username))
    return login.run('echo', private_key=private_key)[0]

def key_present(user,login):
    return user.get_profile().formatted_public_key in login.get_authorized_keys()

def sync_all():
    Login.sync_all()

class NumQueriesTest(TestCase):
    def setUp(self):
        self.users = [create_user(username='user_%d' % i) for i in range(1,4)]
        self.machines = [create_machine() for i in range(10)]
        self.logins = [create_login(username="login_%d" % i, machine=self.machines[i]) for i in range(10)]
        for i in range(10):
            self.logins[i].users = self.users[i:]
            self.logins[i].save()

    def test_access_summary_constant_queries(self):
        request = HttpRequest()
        request.user = create_user(username="ssheepdog", is_superuser=True)
        with self.assertNumQueries(4):
            view_access_summary(request)


class PushKeyTests(TestCase):
    def setUp(self):
        self.user = create_user(username='user_1')
        self.user2 = create_user(username='user_2')
        self.machine = create_machine()
        self.login = create_login(username="login", machine=self.machine)

    def test_machine_inactive(self):
        self.login.users = [self.user]
        self.machine.is_active = False
        self.machine.save()
        self.login.save()
        self.assertFalse(key_present(self.user, self.login))

    def test_user_login_disconnected(self):
        self.assertFalse(key_present(self.user, self.login))

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
        self.machine2 = create_machine()
        self.login = create_login(username="login", machine=self.machine)
        self.login.users = [self.user, self.user2]
        self.login.is_dirty = False
        Login.objects.update(is_dirty=False)
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


    def test_change_machine(self):
        """Switching the machine for another machine dirties"""
        self.login.machine = self.machine2
        self.login.save()
        self.assertDirty()

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

    def test_change_username(self):
        """
        Changing a username does not dirty the login
        """
        self.user.username = "changed username"
        self.user.save()
        self.assertClean()

    def test_change_is_active(self):
        """
        Changing active status effects dirty status
        """
        self.user.is_active = False
        self.user.save()
        self.assertDirty()
        self.login.is_dirty = False
        self.login.save()

        user = User.objects.get(pk=self.user.pk)
        user.save()
        assert(user.is_active == False)
        self.assertClean()

        user.is_active = True
        user.save()
        self.assertDirty()


class ApplicationKeyTests(TestCase):
    def setUp(self):
        populate_ssheepdog_key()
        self.user = create_user(username='user_1')
        self.machine = create_machine()
        self.login = create_login(username="login", machine=self.machine)

    def test_get_latest(self):
        ApplicationKey.objects.create(public_key="A", private_key="A")
        ApplicationKey.objects.create(public_key="B", private_key="B")
        c = ApplicationKey.objects.create(public_key="C", private_key="C")
        latest = ApplicationKey.get_latest()
        self.assertEqual(c, latest)

    def test_get_latest_with_create(self):
        c = ApplicationKey.objects.create(public_key="C", private_key="C")
        latest = ApplicationKey.get_latest()
        self.assertEqual(c, latest)
        latest = ApplicationKey.get_latest(create_new=True)
        self.assertNotEqual(c, latest)

    def test_when_latest_key_differs_from_login_key(self):
        previous = ApplicationKey.get_latest()
        self.assertTrue(previous.formatted_public_key in "\n".join(self.login.get_authorized_keys()))
        latest = ApplicationKey.get_latest(create_new=True)
        keys = "\n".join(self.login.get_authorized_keys())
        self.assertFalse(previous.formatted_public_key in keys)
        self.assertTrue(latest.formatted_public_key in keys)

class PublicKeyFieldTests(TestCase):
    def setUp(self):
        self.field = PublicKeyField()
        self.key = "AAAAB3NzaC1yc2EAAAABIwAAAQEAvRY/4gdg/V6sKShGk/Cx6qqRUiCWybdEokMsTEf502BRe/uD0qP8Y8zQ2fJSPZ5FcySIMorTQ9cl8tSeqVDOhAiwelJW7EB8qCMxc+Nkn8urtXmLTCS26lG/bF5A1XA33ToL3EadLpllUu2oQ8ebetmAuKpjKjVH/oi+ghP2P9yaLOrr6uQT1BGaFTa0dtAN2KSFBNeVejuhbZLgB8/uHEnsdEu3kxeqL9E4WXGbvPKgvrg3J/U6bAMG326yw/C43OHrZEi6OJ+yroRrdKkmHDAHTIZRRgaEkYCXlULBdZMrO2vrIjVTdJSOjeQ324if24L7p3HQx/KOnG4WhMuYbQ=="
    def good(self, key, expected=None):
        result = self.field.clean(key, None)
        if expected:
            self.assertEqual(result, expected)

    def bad(self, key):
        self.assertRaises(exceptions.ValidationError, self.field.clean, key, None)

    def test_good(self):
        self.good("ssh-rsa %s comment" % self.key,
                  "ssh-rsa %s comment" % self.key)

    def test_whitespace_ok(self):
        self.good("  \n\n  ssh-rsa  %s comment  " % self.key,
                  "ssh-rsa %s comment" % self.key)

    def test_two_keys(self):
        self.good("ssh-rsa %s row1\nssh-rsa %s row1" % (self.key, self.key),
                  "ssh-rsa %s row1\nssh-rsa %s row1" % (self.key, self.key))

    def test_two_keys_with_whitespace(self):
        self.good("\nssh-rsa %s row1\n\nssh-rsa  %s  row1\n" % (self.key, self.key),
                  "ssh-rsa %s row1\nssh-rsa %s row1" % (self.key, self.key))


    def test_comment_with_whitespace(self):
        self.good("  \n\n  ssh-rsa  %s comment  comment2  " % self.key,
                  "ssh-rsa %s comment comment2" % self.key)

    def test_no_comment(self):
        self.good("ssh-rsa %s" % self.key, "ssh-rsa %s" % self.key)

    def test_long_enough(self): # This isn't really an ssh key, but it will pass the weak test
        self.good("ssh-rsa %s comment" % self.key[0:104])

    def test_too_short(self):
        self.bad("ssh-rsa %s comment" % self.key[0:96])

    def test_not_base64(self): # This isn't really an ssh key, but it will pass the weak test
        self.bad("ssh-rsa %s comment" % self.key[0:97])

    def test_bad_key_type_name(self):
        self.assertRaises(exceptions.ValidationError, self.field.clean, "sh-rs %s comment" % self.key, None)

