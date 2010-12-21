# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'AboutTopic.short_title'
        db.alter_column('information_abouttopic', 'short_title', self.gf('django.db.models.fields.CharField')(max_length=500, null=True))

        # Changing field 'HelpTopic.short_title'
        db.alter_column('information_helptopic', 'short_title', self.gf('django.db.models.fields.CharField')(max_length=500, null=True))


    def backwards(self, orm):
        
        # Changing field 'AboutTopic.short_title'
        db.alter_column('information_abouttopic', 'short_title', self.gf('django.db.models.fields.CharField')(default=None, max_length=500))

        # Changing field 'HelpTopic.short_title'
        db.alter_column('information_helptopic', 'short_title', self.gf('django.db.models.fields.CharField')(default=None, max_length=500))


    models = {
        'information.abouttopic': {
            'Meta': {'ordering': "['order']", 'object_name': 'AboutTopic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '500', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'information.helptopic': {
            'Meta': {'ordering': "['order']", 'object_name': 'HelpTopic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '500', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        }
    }

    complete_apps = ['information']
