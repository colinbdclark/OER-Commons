# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CountryIPDiapason'
        db.create_table('geo_countryipdiapason', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Country'])),
            ('start', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('end', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('geo', ['CountryIPDiapason'])


    def backwards(self, orm):
        
        # Deleting model 'CountryIPDiapason'
        db.delete_table('geo_countryipdiapason')


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
            'end': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['geo']
