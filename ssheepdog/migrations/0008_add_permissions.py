# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from ssheepdog.utils import add_permission
PERMISSIONS = ( # Managed by South so added by data migration!
    ("can_view_access_summary", "Can view access summary"),
    ("can_sync", "Can sync login keys"),
    ("can_edit_own_public_key", "Can edit one's own public key"),
    )

class Migration(DataMigration):

    def forwards(self, orm):
        ct, created = orm['contenttypes.ContentType'].objects.get_or_create(
            model='login', app_label='ssheepdog')
        for codename, name in PERMISSIONS:
            add_permission(orm, codename, name)

    def backwards(self, orm):
        pass

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ssheepdog.applicationkey': {
            'Meta': {'object_name': 'ApplicationKey'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'private_key': ('django.db.models.fields.TextField', [], {}),
            'public_key': ('ssheepdog.fields.PublicKeyField', [], {})
        },
        'ssheepdog.client': {
            'Meta': {'object_name': 'Client'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'ssheepdog.login': {
            'Meta': {'object_name': 'Login'},
            'application_key': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ssheepdog.ApplicationKey']", 'null': 'True'}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ssheepdog.Client']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_dirty': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'machine': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ssheepdog.Machine']"}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'ssheepdog.loginlog': {
            'Meta': {'object_name': 'LoginLog'},
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'login': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ssheepdog.Login']", 'null': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'stderr': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'stdout': ('django.db.models.fields.TextField', [], {'default': "''"})
        },
        'ssheepdog.machine': {
            'Meta': {'object_name': 'Machine'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ssheepdog.Client']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_down': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '22'})
        },
        'ssheepdog.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ssh_key': ('ssheepdog.fields.PublicKeyField', [], {}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'_profile_cache'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['auth.User']"})
        }
    }
    
    complete_apps = ['ssheepdog']
