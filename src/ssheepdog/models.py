from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserProfile(models.Model):
    nickname = models.CharField(max_length=256)
    user = models.OneToOneField(User, primary_key=True, related_name='_profile_cache')
    ssh_key = models.TextField()
    is_active = models.BooleanField()
    def __str__(self):
        return self.nickname
    def __unicode__(self):
        return self.nickname or self.user.username

class Machine(models.Model):
    # XXX: A machine should have either an IP or hostname or both
    # Need a validator in the form supplied to the django admin
    # Consider validating on save as well... not as important
    nickname = models.CharField(max_length=256)
    hostname = models.CharField(max_length=256, blank=True, null=True)
    ip = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField()
    port = models.IntegerField(default=22)
    client = models.ForeignKey('Client', null=True, blank=True)
    is_active = models.BooleanField()
    def __unicode__(self):
        return self.nickname

class Login(models.Model):
    machine = models.ForeignKey('Machine')
    username = models.CharField(max_length=256)
    users = models.ManyToManyField(User, blank=True)
    client = models.ForeignKey('Client', null=True, blank=True)
    is_active = models.BooleanField()
    def __unicode__(self):
        return self.username
    
class Client(models.Model):
    nickname = models.CharField(max_length=256)
    description = models.TextField()
    def __unicode__(self):
        return self.nickname
