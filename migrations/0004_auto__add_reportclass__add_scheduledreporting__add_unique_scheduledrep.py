# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'ReportClass'
        db.create_table('bolibana_reportclass', (
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=75, primary_key=True, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('cls', self.gf('django.db.models.fields.CharField')(unique=True, max_length=75)),
            ('period_cls', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('report_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('bolibana', ['ReportClass'])

        # Adding model 'ScheduledReporting'
        db.create_table('bolibana_scheduledreporting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('report_class', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bolibana.ReportClass'])),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bolibana.Entity'])),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('start', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='entity_rcls_providers_starting', null=True, to=orm['bolibana.Period'])),
            ('end', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='entity_rcls_providers_ending', null=True, to=orm['bolibana.Period'])),
        ))
        db.send_create_signal('bolibana', ['ScheduledReporting'])

        # Adding unique constraint on 'ScheduledReporting', fields ['report_class', 'entity']
        db.create_unique('bolibana_scheduledreporting', ['report_class_id', 'entity_id'])

        # Adding model 'ExpectedReporting'
        db.create_table('bolibana_expectedreporting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('report_class', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bolibana.ReportClass'])),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bolibana.Entity'])),
            ('period', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bolibana.Period'])),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('bolibana', ['ExpectedReporting'])

        # Adding unique constraint on 'ExpectedReporting', fields ['report_class', 'entity', 'period']
        db.create_unique('bolibana_expectedreporting', ['report_class_id', 'entity_id', 'period_id'])


    def backwards(self, orm):

        # Removing unique constraint on 'ExpectedReporting', fields ['report_class', 'entity', 'period']
        db.delete_unique('bolibana_expectedreporting', ['report_class_id', 'entity_id', 'period_id'])

        # Removing unique constraint on 'ScheduledReporting', fields ['report_class', 'entity']
        db.delete_unique('bolibana_scheduledreporting', ['report_class_id', 'entity_id'])

        # Deleting model 'ReportClass'
        db.delete_table('bolibana_reportclass')

        # Deleting model 'ScheduledReporting'
        db.delete_table('bolibana_scheduledreporting')

        # Deleting model 'ExpectedReporting'
        db.delete_table('bolibana_expectedreporting')


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
        'bolibana.access': {
            'Meta': {'unique_together': "(('role', 'content_type', 'object_id'),)", 'object_name': 'Access'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bolibana.Role']"})
        },
        'bolibana.entity': {
            'Meta': {'object_name': 'Entity'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['bolibana.Entity']"}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '12', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '15', 'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entities'", 'to': "orm['bolibana.EntityType']"})
        },
        'bolibana.entitytype': {
            'Meta': {'object_name': 'EntityType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '15', 'db_index': 'True'})
        },
        'bolibana.expectedreporting': {
            'Meta': {'unique_together': "(('report_class', 'entity', 'period'),)", 'object_name': 'ExpectedReporting'},
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bolibana.Entity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bolibana.Period']"}),
            'report_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bolibana.ReportClass']"})
        },
        'bolibana.period': {
            'Meta': {'unique_together': "(('start_on', 'end_on', 'period_type'),)", 'object_name': 'Period'},
            'end_on': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period_type': ('django.db.models.fields.CharField', [], {'default': "'custom'", 'max_length': '15'}),
            'start_on': ('django.db.models.fields.DateTimeField', [], {})
        },
        'bolibana.permission': {
            'Meta': {'object_name': 'Permission'},
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'primary_key': 'True', 'db_index': 'True'})
        },
        'bolibana.provider': {
            'Meta': {'object_name': 'Provider'},
            'access': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['bolibana.Access']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '12', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'phone_number_extra': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'pwhash': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'bolibana.reportclass': {
            'Meta': {'object_name': 'ReportClass'},
            'cls': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'period_cls': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'report_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '75', 'primary_key': 'True', 'db_index': 'True'})
        },
        'bolibana.role': {
            'Meta': {'object_name': 'Role'},
            'level': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['bolibana.Permission']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '15', 'primary_key': 'True', 'db_index': 'True'})
        },
        'bolibana.scheduledreporting': {
            'Meta': {'unique_together': "(('report_class', 'entity'),)", 'object_name': 'ScheduledReporting'},
            'end': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'entity_rcls_providers_ending'", 'null': 'True', 'to': "orm['bolibana.Period']"}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bolibana.Entity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'report_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bolibana.ReportClass']"}),
            'start': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'entity_rcls_providers_starting'", 'null': 'True', 'to': "orm['bolibana.Period']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['bolibana']
