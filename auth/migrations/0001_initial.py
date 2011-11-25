# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Role'
        db.create_table('bolibana_auth_role', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=15, primary_key=True, db_index=True)),
        ))
        db.send_create_signal('bolibana_auth', ['Role'])

        # Adding M2M table for field permissions on 'Role'
        db.create_table('bolibana_auth_role_permissions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('role', models.ForeignKey(orm['bolibana_auth.role'], null=False)),
            ('permission', models.ForeignKey(orm['bolibana_auth.permission'], null=False))
        ))
        db.create_unique('bolibana_auth_role_permissions', ['role_id', 'permission_id'])

        # Adding model 'Provider'
        db.create_table('bolibana_auth_provider', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=12, unique=True, null=True, blank=True)),
        ))
        db.send_create_signal('bolibana_auth', ['Provider'])

        # Adding M2M table for field access on 'Provider'
        db.create_table('bolibana_auth_provider_access', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('provider', models.ForeignKey(orm['bolibana_auth.provider'], null=False)),
            ('access', models.ForeignKey(orm['bolibana_auth.access'], null=False))
        ))
        db.create_unique('bolibana_auth_provider_access', ['provider_id', 'access_id'])

        # Adding model 'Access'
        db.create_table('bolibana_auth_access', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bolibana_auth.Role'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('bolibana_auth', ['Access'])

        # Adding unique constraint on 'Access', fields ['role', 'content_type', 'object_id']
        db.create_unique('bolibana_auth_access', ['role_id', 'content_type_id', 'object_id'])

        # Adding model 'Permission'
        db.create_table('bolibana_auth_permission', (
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, primary_key=True, db_index=True)),
        ))
        db.send_create_signal('bolibana_auth', ['Permission'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Access', fields ['role', 'content_type', 'object_id']
        db.delete_unique('bolibana_auth_access', ['role_id', 'content_type_id', 'object_id'])

        # Deleting model 'Role'
        db.delete_table('bolibana_auth_role')

        # Removing M2M table for field permissions on 'Role'
        db.delete_table('bolibana_auth_role_permissions')

        # Deleting model 'Provider'
        db.delete_table('bolibana_auth_provider')

        # Removing M2M table for field access on 'Provider'
        db.delete_table('bolibana_auth_provider_access')

        # Deleting model 'Access'
        db.delete_table('bolibana_auth_access')

        # Deleting model 'Permission'
        db.delete_table('bolibana_auth_permission')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'bolibana_auth.access': {
            'Meta': {'unique_together': "(('role', 'content_type', 'object_id'),)", 'object_name': 'Access'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bolibana_auth.Role']"})
        },
        'bolibana_auth.permission': {
            'Meta': {'object_name': 'Permission'},
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'primary_key': 'True', 'db_index': 'True'})
        },
        'bolibana_auth.provider': {
            'Meta': {'object_name': 'Provider'},
            'access': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['bolibana_auth.Access']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '12', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'bolibana_auth.role': {
            'Meta': {'object_name': 'Role'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['bolibana_auth.Permission']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '15', 'primary_key': 'True', 'db_index': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['bolibana_auth']
