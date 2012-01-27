import os, base64, struct
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed
from django.db.utils import DatabaseError
from fabric.api import env, run, hide, settings
from fabric.network import disconnect_all
from django.conf import settings as app_settings
from ssheepdog.utils import DirtyFieldsMixin
from django.core.urlresolvers import reverse
from south.signals import post_migrate
from south.modelsinspector import add_introspection_rules
from django.core import exceptions
from django.utils.translation import ugettext as _
from Crypto.PublicKey import RSA
add_introspection_rules([], ["^ssheepdog\.fields\.PublicKeyField"])

KEYS_DIR = os.path.join(app_settings.PROJECT_ROOT,
                        '../deploy/keys')
FABRIC_WARNINGS = ['everything', 'status', 'aborts']


class PublicKeyField(models.TextField):
    def validate(self, value, model_instance):
        """
        Just confirm that the first field is something like ssh-rsa or ssh-dss,
        and the second field is reasonably long and can be base64 decoded.
        """
        super(PublicKeyField, self).validate(value, model_instance)
        try:
            type_, key_string = value.split()[:2]
            assert (type_[:4] == 'ssh-')
            assert (len(key_string) > 100)
            base64.decodestring(key_string)
        except:
            raise exceptions.ValidationError(_("Does not appear to be an ssh public key"))
        
    def clean(self, value, model_instance):
        """
        Clean up any whitespace.
        """
        value = " ".join(value.strip().split())
        return super(PublicKeyField, self).clean(value, model_instance)


class UserProfile(DirtyFieldsMixin, models.Model):
    nickname = models.CharField(max_length=256)
    user = models.OneToOneField(User, primary_key=True, related_name='_profile_cache')
    ssh_key = PublicKeyField()

    def __str__(self):
        return self.nickname

    def __unicode__(self):
        return self.nickname or self.user.username


class Machine(DirtyFieldsMixin, models.Model):
    # XXX: A machine should have either an IP or hostname or both
    # Need a validator in the form supplied to the django admin
    # Consider validating on save as well... not as important
    nickname = models.CharField(max_length=256)
    hostname = models.CharField(max_length=256, blank=True, null=True)
    ip = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField()
    port = models.IntegerField(default=22)
    client = models.ForeignKey('Client', null=True, blank=True)
    is_down = models.BooleanField(default=False)
    is_active = models.BooleanField()

    def __unicode__(self):
        return self.nickname

    def save(self, *args, **kwargs):
        fields = set(['hostname', 'ip', 'port','is_active'])
        made_dirty = bool(fields.intersection(self.get_dirty_fields()))
        if made_dirty:
            self.login_set.update(is_dirty=True)
        super(Machine, self).save(*args, **kwargs)


class Login(DirtyFieldsMixin, models.Model):
    machine = models.ForeignKey('Machine')
    username = models.CharField(max_length=256)
    users = models.ManyToManyField(User, blank=True)
    client = models.ForeignKey('Client', null=True, blank=True)
    application_key = models.ForeignKey('ApplicationKey', null=True)
    is_active = models.BooleanField(default=True)
    is_dirty = models.BooleanField(default=True)

    def get_change_url(self):
        return reverse('admin:ssheepdog_login_change', args=(self.pk,))

    @staticmethod
    def sync_all():
        try:
            for login in Login.objects.all():
                login.sync()
        finally:
            disconnect_all()

    def sync(self):
        self.update_keys()
        disconnect_all()

    def __unicode__(self):
        return self.username
    
    def get_application_key(self):
        if self.application_key is None:
            self.application_key = ApplicationKey.get_latest()
            self.save()
        return self.application_key

    @property
    def formatted_public_key(self):
        return self.get_application_key().formatted_public_key

    def save(self, *args, **kwargs):
        fields = set(['machine', 'username', 'is_active'])
        made_dirty = bool(fields.intersection(self.get_dirty_fields()))
        self.is_dirty = self.is_dirty or made_dirty
        super(Login, self).save(*args, **kwargs)

    def run(self, command, private_key=None):
        """
        Ssh in to Login to run command.  Return True on success, False ow.
        """
        mach = self.machine
        env.abort_on_prompts = True
        env.key_filename = private_key or ApplicationKey.get_latest().private_key
        env.host_string = "%s@%s:%d" % (self.username,
                                        (mach.ip or mach.hostname),
                                        mach.port)    
        try:
            with settings(hide(*FABRIC_WARNINGS)):
                run(command)
            return True
        except SystemExit:
            return False

    def get_authorized_keys(self):
        """
        Return a list of authorized keys strings which should be deployed
        to the machine.
        """
        keys = [ApplicationKey.get_latest().formatted_public_key] 
        if self.is_active and self.machine.is_active:
            for user in (self.users
                         .filter(is_active = True)
                         .select_related('_profile_cache')):
                keys.append(user.get_profile().ssh_key)
        return keys

    def update_keys(self): 
        """
        Updates the authorized_keys file on the machine attached to this login 
        adding or deleting users public keys

        Returns True if successfully changed the authorized files and False if
        not (status stays dirty).  If no change attempted, return None.
        """
        if self.machine.is_down or not self.is_dirty:
            # No update required (either impossible or not needed)
            return None
        if self.run('echo "%s" > ~/.ssh/authorized_keys' % "\n\n".join(
            self.get_authorized_keys()),
            self.get_application_key().private_key):
            self.is_dirty = False
            self.application_key = ApplicationKey.get_latest() 
            self.save()
            return True
        else:
            return False


class Client(models.Model):
    nickname = models.CharField(max_length=256)
    description = models.TextField()
    def __unicode__(self):
        return self.nickname


class ApplicationKey(models.Model):
    private_key = models.TextField()
    public_key = PublicKeyField()

    def save(self, *args, **kwargs):
        if not self.private_key or not self.public_key:
            self.generate_key_pair()
        self.private_key = self.private_key.strip()
        self.public_key = self.public_key.strip()
        super(ApplicationKey, self).save(*args, **kwargs)

    @property
    def formatted_public_key(self):
        return "%s ssheepdog_%s" % (self.public_key, self.pk)

    def __unicode__(self):
        return "...%s ssheepdog_%s" % (self.public_key[-10:], self.pk)

    def generate_key_pair(self):
        key = RSA.generate(app_settings.RSA_KEY_LENGTH)
        self.private_key = key.exportKey()

        # This magic is from
        # http://stackoverflow.com/questions/2466401/how-to-generate-ssh-key-pairs-with-python

        exponent = '%x' % (key.e, )
        if len(exponent) % 2:
            exponent = '0' + exponent
        
        ssh_rsa = '00000007' + base64.b16encode('ssh-rsa')
        ssh_rsa += '%08x' % (len(exponent) / 2, )
        ssh_rsa += exponent
        
        modulus = '%x' % (key.n, )
        if len(modulus) % 2:
            modulus = '0' + modulus
        
        if modulus[0] in '89abcdef':
            modulus = '00' + modulus
        
        ssh_rsa += '%08x' % (len(modulus) / 2, )
        ssh_rsa += modulus
        
        self.public_key = 'ssh-rsa %s' % (
            base64.b64encode(base64.b16decode(ssh_rsa.upper())),
            )
        
    @staticmethod
    def get_latest(create_new=False):
        if not create_new:
            try:
                return ApplicationKey.objects.latest('pk')
            except ApplicationKey.DoesNotExist:
                pass
        key = ApplicationKey()
        key.save()
        return key


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            UserProfile.objects.create(user=instance)
        except DatabaseError: # Creating fresh db from manage.py
            pass


post_save.connect(create_user_profile, sender=User)


def user_login_changed(sender, instance=None, reverse=None, model=None,
                       action=None, **kwargs):
    if action[:4] == 'pre_':
        return
    login = model if reverse else instance
    login.is_dirty = True
    login.save()


m2m_changed.connect(user_login_changed, sender=Login.users.through)


def force_one_app_key(app, **kwargs):
    if app == 'ssheepdog':
        ApplicationKey.get_latest()         

post_migrate.connect(force_one_app_key)

