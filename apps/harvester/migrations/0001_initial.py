# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Repository'
        db.create_table('harvester_repository', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('base_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('protocol_version', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('earliest_datestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('deleted_record', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('granularity', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('harvester', ['Repository'])

        # Adding model 'Set'
        db.create_table('harvester_set', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('repository', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['harvester.Repository'])),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('harvester', ['Set'])

        # Adding model 'AdminEmail'
        db.create_table('harvester_adminemail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('repository', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['harvester.Repository'])),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=200)),
        ))
        db.send_create_signal('harvester', ['AdminEmail'])

        # Adding model 'MetadataPrefix'
        db.create_table('harvester_metadataprefix', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('repository', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['harvester.Repository'])),
            ('prefix', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('harvester', ['MetadataPrefix'])

        # Adding model 'Job'
        db.create_table('harvester_job', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('repository', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['harvester.Repository'])),
            ('metadata_prefix', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['harvester.MetadataPrefix'])),
            ('from_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('until_data', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=200)),
            ('processed_records', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('harvested_records', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
        ))
        db.send_create_signal('harvester', ['Job'])

        # Adding M2M table for field sets on 'Job'
        db.create_table('harvester_job_sets', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('job', models.ForeignKey(orm['harvester.job'], null=False)),
            ('set', models.ForeignKey(orm['harvester.set'], null=False))
        ))
        db.create_unique('harvester_job_sets', ['job_id', 'set_id'])

        # Adding model 'Error'
        db.create_table('harvester_error', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['harvester.Job'])),
        ))
        db.send_create_signal('harvester', ['Error'])


    def backwards(self, orm):
        
        # Deleting model 'Repository'
        db.delete_table('harvester_repository')

        # Deleting model 'Set'
        db.delete_table('harvester_set')

        # Deleting model 'AdminEmail'
        db.delete_table('harvester_adminemail')

        # Deleting model 'MetadataPrefix'
        db.delete_table('harvester_metadataprefix')

        # Deleting model 'Job'
        db.delete_table('harvester_job')

        # Removing M2M table for field sets on 'Job'
        db.delete_table('harvester_job_sets')

        # Deleting model 'Error'
        db.delete_table('harvester_error')


    models = {
        'harvester.adminemail': {
            'Meta': {'object_name': 'AdminEmail'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['harvester.Repository']"})
        },
        'harvester.error': {
            'Meta': {'object_name': 'Error'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['harvester.Job']"}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'harvester.job': {
            'Meta': {'object_name': 'Job'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '200'}),
            'from_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'harvested_records': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata_prefix': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['harvester.MetadataPrefix']"}),
            'processed_records': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['harvester.Repository']"}),
            'sets': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['harvester.Set']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'until_data': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'harvester.metadataprefix': {
            'Meta': {'object_name': 'MetadataPrefix'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['harvester.Repository']"})
        },
        'harvester.repository': {
            'Meta': {'object_name': 'Repository'},
            'base_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'deleted_record': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'earliest_datestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'granularity': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'protocol_version': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'harvester.set': {
            'Meta': {'object_name': 'Set'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['harvester.Repository']"})
        }
    }

    complete_apps = ['harvester']
