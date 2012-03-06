import os, base64
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed
from django.db.utils import DatabaseError
from fabric.api import env, run, hide, settings
from fabric.network import disconnect_all
from django.conf import settings as app_settings
from ssheepdog.utils import DirtyFieldsMixin, capture_output
from django.core.urlresolvers import reverse
from south.signals import post_migrate
from south.modelsinspector import add_introspection_rules
from Crypto.PublicKey import RSA
from ssheepdog.fields import PublicKeyField
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

add_introspection_rules([], ["^ssheepdog\.fields\.PublicKeyField"])

KEYS_DIR = os.path.join(app_settings.PROJECT_ROOT,
                        '../deploy/keys')
ALL_FABRIC_WARNINGS = ['everything', 'status', 'aborts']
FABRIC_WARNINGS = []

class UserProfile(DirtyFieldsMixin, models.Model):
    nickname = models.CharField(max_length=256)
    user = models.OneToOneField(User, primary_key=True, related_name='_profile_cache')
    ssh_key = PublicKeyField(blank=True)

    @property
    def formatted_public_key(self):
        name = self.user.get_full_name()
        return "## %s%s\n%s" % (self.user.email or self.user.username,
                                " (%s)" % name if name else "",
                                self.ssh_key)

    def __str__(self):
        return self.nickname

    def __unicode__(self):
        return self.nickname or self.user.username

    def save(self, *args, **kwargs):
        if 'ssh_key' in self.get_dirty_fields():
            Login.objects.filter(users___profile_cache=self).update(is_dirty=True)

        super(UserProfile, self).save(*args, **kwargs)


class Machine(DirtyFieldsMixin, models.Model):
    nickname = models.CharField(max_length=256)
    hostname = models.CharField(max_length=256, blank=True, null=True)
    ip = models.CharField(max_length=256, null=True, blank=True,
                          help_text="If you supply both an ip and a hostname,"
                          " the ip will be used for key deployments.")
    description = models.TextField()
    port = models.IntegerField(default=22)
    client = models.ForeignKey('Client', null=True, blank=True)
    is_down = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    manual = models.BooleanField(
        default=False,
        verbose_name="Requires manual deployments",
        help_text="This machine requires manual key deployments.  For example,"
        " it may be behind a firewall and ssheepdog lacks ssh access.")

    def __unicode__(self):
        if self.hostname and self.ip:
            parenthetical = "%s, %s" % (self.hostname, self.ip)
        else:
            parenthetical = self.hostname or self.ip
        return "%s (%s)" % (self.nickname, parenthetical)

    def get_change_url(self):
        return reverse('admin:ssheepdog_machine_change', args=(self.pk,))

    def clean(self, *args, **kwargs):
        if not self.ip and not self.hostname:
            raise ValidationError("Provide an ip or a hostname or both")

    def save(self, *args, **kwargs):
        dirty_fields = self.get_dirty_fields()

        # Updates to these fields require a push of keys to all logins
        fields = set(['hostname', 'ip', 'port', 'is_active'])
        made_dirty = bool(fields.intersection(dirty_fields))
        if made_dirty:
            self.login_set.update(is_dirty=True)

        super(Machine, self).save(*args, **kwargs)

        # if the client changed, make login clients change which used to match
        if 'client_pk' in dirty_fields:
            old_pk = dirty_fields['client_pk']
            self.login_set.filter(client__pk=old_pk).update(client=self.client)
            self.login_set.filter(client__pk=None).update(client=self.client)


class LoginLog(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    stderr = models.TextField(default="")
    stdout = models.TextField(default="")
    login = models.ForeignKey('Login', null=True)
    actor = models.ForeignKey(User, null=True)
    class Meta:
        ordering = ['-date']


class Login(DirtyFieldsMixin, models.Model):
    machine = models.ForeignKey('Machine')
    username = models.CharField(max_length=256)
    users = models.ManyToManyField(User, blank=True)
    client = models.ForeignKey('Client', null=True, blank=True)
    application_key = models.ForeignKey('ApplicationKey', null=True, verbose_name="SSHeepdog Public Key")
    is_active = models.BooleanField(default=True)
    is_dirty = models.BooleanField(default=True)
    additional_public_keys = PublicKeyField(blank=True,
        help_text=_("These are public keys which will be pushed to the login"
                    " in addition to user keys."))

    class Meta:
        ordering = ('username', 'client__nickname',)

        permissions = ( # Managed by South so added by data migration!
            ("can_view_access_summary", "Can view access summary"),
            ("can_sync", "Can sync login keys"),
            ("can_edit_own_public_key", "Can edit one's own public key"),
            ("can_view_all_users", "Can view other users"),
            ("can_view_all_logins", "Can view other's logins"),
            )

    def get_address(self):
        return "%s@%s" % (self.username, self.machine.ip or self.machine.hostname)

    def get_last_log(self):
        try:
            return LoginLog.objects.filter(login=self).latest('date')
        except LoginLog.DoesNotExist:
            return None

    def get_change_url(self):
        return reverse('admin:ssheepdog_login_change', args=(self.pk,))

    @staticmethod
    def sync_all(actor=None):
        try:
            for login in Login.objects.exclude(machine__manual=True):
                login.sync(actor=actor)
        finally:
            with settings(hide(*ALL_FABRIC_WARNINGS)):
                disconnect_all()

    def __unicode__(self):
        if self.client:
            return "%s@%s (%s)" % (self.username,
                                   self.machine.hostname or self.machine.ip,
                                   self.client)
        else:
            return "%s@%s" % (self.username, self.machine)

    def get_application_key(self):
        if self.application_key is None:
            self.application_key = ApplicationKey.get_latest()
            self.save()
        return self.application_key

    @property
    def formatted_public_key(self):
        return self.get_application_key().formatted_public_key

    def save(self, *args, **kwargs):
        if not self.client:
            self.client = self.machine.client

        # Updates to these fields require a push of keys to login
        fields = set(['machine_pk', 'username', 'is_active'])
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
            with capture_output() as captured:
                run(command)
            return True, captured
        except SystemExit:
            return False, captured

    def get_client(self):
        return self.client or self.machine.client

    def get_authorized_keys(self):
        """
        Return a list of authorized keys strings which should be deployed
        to the machine.
        """
        keys = ["%s\n%s" %
                ("######################################################\n"
                 "### This public keys file is managed by ssheepdog. ###\n"
                 "### Changes made manually will be overwritten.     ###\n"
                 "######################################################",
                 ApplicationKey.get_latest().formatted_public_key)]
        if self.is_active and self.machine.is_active:
            if self.additional_public_keys:
                keys.append("## Additional keys specified in Login\n%s"
                            % self.additional_public_keys)
            for user in (self.users
                         .filter(is_active = True)
                         .select_related('_profile_cache')):
                keys.append(user.get_profile().formatted_public_key)
        return keys

    def formatted_keys(self):
        formatted_keys = "\n\n".join(self.get_authorized_keys())
        # Switch back and forth between ' and "" to quote '
        return formatted_keys.replace("'", "'\"'\"'")

    def flag_as_manually_synced_by(self, actor):
        self.is_dirty = False
        self.application_key = ApplicationKey.get_latest()
        self.save()
        LoginLog.objects.create(actor=actor,
                                login=self,
                                message="Manual sync was performed")

    def sync(self, actor=None):
        """
        Updates the authorized_keys file on the machine attached to this login
        adding or deleting users public keys

        Returns True if successfully changed the authorized files and False if
        not (status stays dirty).  If no change attempted, return None.
        """
        if self.machine.is_down or self.machine.manual or not self.is_dirty:
            # No update required (either impossible or not needed)
            return None
        success, output = self.run("echo '%s' > ~/.ssh/authorized_keys" % self.formatted_keys(),
                                   self.get_application_key().private_key)

        message="%successful %s" % ("S" if success else "Uns",
                                    "key deployment")
        LoginLog.objects.create(stderr=output.stderr,
                                stdout=output.stdout,
                                actor=actor,
                                login=self,
                                message=message
                                )

        with settings(hide(*ALL_FABRIC_WARNINGS)):
            disconnect_all()

        if success:
            self.is_dirty = False
            self.application_key = ApplicationKey.get_latest()
            self.save()
            return True
        else:
            return False


class Client(models.Model):
    nickname = models.CharField(max_length=256)
    description = models.TextField()

    def get_change_url(self):
        return reverse('admin:ssheepdog_client_change', args=(self.pk,))

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

