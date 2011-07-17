# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Country'
        db.create_table('geo_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=100, populate_from=None, unique_with=(), db_index=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=2, db_index=True)),
        ))
        db.send_create_signal('geo', ['Country'])


    def backwards(self, orm):
        
        # Deleting model 'Country'
        db.delete_table('geo_country')


    models = {
        'geo.country': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        }
    }

    complete_apps = ['geo']
