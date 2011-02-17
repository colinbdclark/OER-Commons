# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'MetadataPrefix.schema'
        db.add_column('harvester_metadataprefix', 'schema', self.gf('django.db.models.fields.CharField')(default=None, max_length=200), keep_default=False)

        # Adding field 'MetadataPrefix.namespace'
        db.add_column('harvester_metadataprefix', 'namespace', self.gf('django.db.models.fields.CharField')(default=None, max_length=200), keep_default=False)

        # Deleting field 'Set.identifier'
        db.delete_column('harvester_set', 'identifier')

        # Adding field 'Set.spec'
        db.add_column('harvester_set', 'spec', self.gf('django.db.models.fields.CharField')(default=None, max_length=200), keep_default=False)

        # Changing field 'Repository.name'
        db.alter_column('harvester_repository', 'name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True))

        # Changing field 'Repository.earliest_datestamp'
        db.alter_column('harvester_repository', 'earliest_datestamp', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'Repository.granularity'
        db.alter_column('harvester_repository', 'granularity', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'Repository.protocol_version'
        db.alter_column('harvester_repository', 'protocol_version', self.gf('django.db.models.fields.CharField')(max_length=10, null=True))

        # Changing field 'Repository.deleted_record'
        db.alter_column('harvester_repository', 'deleted_record', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))


    def backwards(self, orm):
        
        # Deleting field 'MetadataPrefix.schema'
        db.delete_column('harvester_metadataprefix', 'schema')

        # Deleting field 'MetadataPrefix.namespace'
        db.delete_column('harvester_metadataprefix', 'namespace')

        # User chose to not deal with backwards NULL issues for 'Set.identifier'
        raise RuntimeError("Cannot reverse this migration. 'Set.identifier' and its values cannot be restored.")

        # Deleting field 'Set.spec'
        db.delete_column('harvester_set', 'spec')

        # User chose to not deal with backwards NULL issues for 'Repository.name'
        raise RuntimeError("Cannot reverse this migration. 'Repository.name' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Repository.earliest_datestamp'
        raise RuntimeError("Cannot reverse this migration. 'Repository.earliest_datestamp' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Repository.granularity'
        raise RuntimeError("Cannot reverse this migration. 'Repository.granularity' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Repository.protocol_version'
        raise RuntimeError("Cannot reverse this migration. 'Repository.protocol_version' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Repository.deleted_record'
        raise RuntimeError("Cannot reverse this migration. 'Repository.deleted_record' and its values cannot be restored.")


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
            'Meta': {'object_name': 'Set'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sets'", 'to': "orm['harvester.Repository']"}),
            'spec': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['harvester']
