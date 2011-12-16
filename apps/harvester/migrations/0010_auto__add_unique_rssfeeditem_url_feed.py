# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding unique constraint on 'RSSFeedItem', fields ['url', 'feed']
        db.create_unique('harvester_rssfeeditem', ['url', 'feed_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'RSSFeedItem', fields ['url', 'feed']
        db.delete_unique('harvester_rssfeeditem', ['url', 'feed_id'])


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
        'harvester.rssfeed': {
            'Meta': {'ordering': "('id',)", 'object_name': 'RSSFeed'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '1000', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '1000'})
        },
        'harvester.rssfeeditem': {
            'Meta': {'unique_together': "(('url', 'feed'),)", 'object_name': 'RSSFeedItem'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'None'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'exported': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['harvester.RSSFeed']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '1000'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '1000'})
        },
        'harvester.set': {
            'Meta': {'ordering': "['repository', 'spec', 'name']", 'object_name': 'Set'},
            'harvested_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sets'", 'to': "orm['harvester.Repository']"}),
            'spec': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['harvester']
