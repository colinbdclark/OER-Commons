# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Job.created_at'
        db.add_column('harvester_job', 'created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.now(), blank=True), keep_default=False)

        # Adding field 'Job.finished_at'
        db.add_column('harvester_job', 'finished_at', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Job.created_at'
        db.delete_column('harvester_job', 'created_at')

        # Deleting field 'Job.finished_at'
        db.delete_column('harvester_job', 'finished_at')


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
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '200'}),
            'finished_at': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
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
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'metadata_prefixes'", 'to': "orm['harvester.Repository']"})
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
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sets'", 'to': "orm['harvester.Repository']"})
        }
    }

    complete_apps = ['harvester']
