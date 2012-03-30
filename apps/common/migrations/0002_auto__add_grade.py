# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Grade'
        db.create_table('common_grade', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10, db_index=True)),
        ))
        db.send_create_signal('common', ['Grade'])


    def backwards(self, orm):
        
        # Deleting model 'Grade'
        db.delete_table('common_grade')


    models = {
        'common.grade': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Grade'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'common.studentlevel': {
            'Meta': {'ordering': "('id',)", 'object_name': 'StudentLevel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['common']
