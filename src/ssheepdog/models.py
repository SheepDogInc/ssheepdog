from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed
from django.db.utils import DatabaseError
from fabric.api import env, run, hide, settings
import os
from django.conf import settings as app_settings
from ssheepdog.utils import read_file, DirtyFieldsMixin

KEYS_DIR = os.path.join(app_settings.PROJECT_ROOT,
                        '../deploy/keys')
FABRIC_WARNINGS = ['everything', 'status', 'aborts']

class UserProfile(DirtyFieldsMixin, models.Model):
    nickname = models.CharField(max_length=256)
    user = models.OneToOneField(User, primary_key=True, related_name='_profile_cache')
    ssh_key = models.TextField()
    is_active = models.BooleanField()

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
    is_active = models.BooleanField(default=True)
    is_dirty = models.BooleanField(default=True)

    def __unicode__(self):
        return self.username

    def save(self, *args, **kwargs):
        fields = set(['machine', 'username', 'is_active'])
        made_dirty = bool(fields.intersection(self.get_dirty_fields()))
        self.is_dirty = self.is_dirty or made_dirty
        super(Login, self).save(*args, **kwargs)

    def run(self, command, private_key_filename='ssheepdog'):
        """
        Ssh in to Login to run command.  Return True on success, False ow.
        """
        mach = self.machine
        env.abort_on_prompts = True
        env.key_filename = os.path.join(KEYS_DIR, private_key_filename)
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
        keys = [read_file(os.path.join(KEYS_DIR, 'ssheepdog.pub'))]
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
        if self.run('echo "%s" > ~/.ssh/authorized_keys' % "\n".join(
            self.get_authorized_keys())):
            self.is_dirty = False
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
    public_key = models.TextField()

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
