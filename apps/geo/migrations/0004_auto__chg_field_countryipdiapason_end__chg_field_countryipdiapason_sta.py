# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'CountryIPDiapason.end'
        db.alter_column('geo_countryipdiapason', 'end', self.gf('django.db.models.fields.BigIntegerField')())

        # Changing field 'CountryIPDiapason.start'
        db.alter_column('geo_countryipdiapason', 'start', self.gf('django.db.models.fields.BigIntegerField')())


    def backwards(self, orm):
        
        # Changing field 'CountryIPDiapason.end'
        db.alter_column('geo_countryipdiapason', 'end', self.gf('django.db.models.fields.PositiveIntegerField')())

        # Changing field 'CountryIPDiapason.start'
        db.alter_column('geo_countryipdiapason', 'start', self.gf('django.db.models.fields.PositiveIntegerField')())


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
            'end': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['geo']
