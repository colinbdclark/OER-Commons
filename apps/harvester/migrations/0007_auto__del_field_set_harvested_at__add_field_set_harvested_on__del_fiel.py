# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Set.harvested_at'
        db.delete_column('harvester_set', 'harvested_at')

        # Adding field 'Set.harvested_on'
        db.add_column('harvester_set', 'harvested_on', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)

        # Deleting field 'Job.finished_at'
        db.delete_column('harvester_job', 'finished_at')

        # Deleting field 'Job.created_at'
        db.delete_column('harvester_job', 'created_at')

        # Adding field 'Job.created_on'
        db.add_column('harvester_job', 'created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.now(), blank=True), keep_default=False)

        # Adding field 'Job.finished_on'
        db.add_column('harvester_job', 'finished_on', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'Set.harvested_at'
        db.add_column('harvester_set', 'harvested_at', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)

        # Deleting field 'Set.harvested_on'
        db.delete_column('harvester_set', 'harvested_on')

        # Adding field 'Job.finished_at'
        db.add_column('harvester_job', 'finished_at', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)

        # User chose to not deal with backwards NULL issues for 'Job.created_at'
        raise RuntimeError("Cannot reverse this migration. 'Job.created_at' and its values cannot be restored.")

        # Deleting field 'Job.created_on'
        db.delete_column('harvester_job', 'created_on')

        # Deleting field 'Job.finished_on'
        db.delete_column('harvester_job', 'finished_on')


    models = {
        'harvester.adminemail': {
            'Meta': {'object_name': 'AdminEmail'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'admin_emails'", 'to': "orm['harvester.Repository']"})
        },
        'harvester.error': {
            'Meta': {'object_name': 'Error'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'errors'", 'to': "orm['harvester.Job']"}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'harvester.job': {
            'Meta': {'object_name': 'Job'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '200'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'finished_on': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'from_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'harvested_records': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata_prefix': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['harvester.MetadataPrefix']"}),
            'processed_records': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['harvester.Repository']"}),
            'set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['harvester.Set']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'until_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'harvester.metadataprefix': {
            'Meta': {'ordering': "['repository', 'prefix']", 'object_name': 'MetadataPrefix'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'namespace': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'metadata_prefixes'", 'to': "orm['harvester.Repository']"}),
            'schema': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'harvester.repository': {
            'Meta': {'object_name': 'Repository'},
            'base_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'deleted_record': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'earliest_datestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'granularity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'protocol_version': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'harvester.set': {
            'Meta': {'ordering': "['repository', 'spec', 'name']", 'object_name': 'Set'},
            'harvested_on': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sets'", 'to': "orm['harvester.Repository']"}),
            'spec': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['harvester']
