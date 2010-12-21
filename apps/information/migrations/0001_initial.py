# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'HelpTopic'
        db.create_table('information_helptopic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('short_title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=500, populate_from=None, unique_with=(), db_index=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('information', ['HelpTopic'])

        # Adding model 'AboutTopic'
        db.create_table('information_abouttopic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('short_title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=500, populate_from=None, unique_with=(), db_index=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('information', ['AboutTopic'])


    def backwards(self, orm):
        
        # Deleting model 'HelpTopic'
        db.delete_table('information_helptopic')

        # Deleting model 'AboutTopic'
        db.delete_table('information_abouttopic')


    models = {
        'information.abouttopic': {
            'Meta': {'ordering': "['order']", 'object_name': 'AboutTopic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '500', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'information.helptopic': {
            'Meta': {'ordering': "['order']", 'object_name': 'HelpTopic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '500', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        }
    }

    complete_apps = ['information']
