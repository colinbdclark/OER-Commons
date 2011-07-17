# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding index on 'CountryIPDiapason', fields ['end']
        db.create_index('geo_countryipdiapason', ['end'])

        # Adding index on 'CountryIPDiapason', fields ['start']
        db.create_index('geo_countryipdiapason', ['start'])


    def backwards(self, orm):
        
        # Removing index on 'CountryIPDiapason', fields ['start']
        db.delete_index('geo_countryipdiapason', ['start'])

        # Removing index on 'CountryIPDiapason', fields ['end']
        db.delete_index('geo_countryipdiapason', ['end'])


    models = {
        'geo.country': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'geo.countryipdiapason': {
            'Meta': {'ordering': "('country',)", 'object_name': 'CountryIPDiapason'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Country']"}),
            'end': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['geo']
