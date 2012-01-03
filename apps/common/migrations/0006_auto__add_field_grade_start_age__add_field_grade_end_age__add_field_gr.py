# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Grade.start_age'
        db.add_column('common_grade', 'start_age', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Grade.end_age'
        db.add_column('common_grade', 'end_age', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'GradeSubLevel.start_age'
        db.add_column('common_gradesublevel', 'start_age', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'GradeSubLevel.end_age'
        db.add_column('common_gradesublevel', 'end_age', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'GradeLevel.start_age'
        db.add_column('common_gradelevel', 'start_age', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'GradeLevel.end_age'
        db.add_column('common_gradelevel', 'end_age', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Grade.start_age'
        db.delete_column('common_grade', 'start_age')

        # Deleting field 'Grade.end_age'
        db.delete_column('common_grade', 'end_age')

        # Deleting field 'GradeSubLevel.start_age'
        db.delete_column('common_gradesublevel', 'start_age')

        # Deleting field 'GradeSubLevel.end_age'
        db.delete_column('common_gradesublevel', 'end_age')

        # Deleting field 'GradeLevel.start_age'
        db.delete_column('common_gradelevel', 'start_age')

        # Deleting field 'GradeLevel.end_age'
        db.delete_column('common_gradelevel', 'end_age')


    models = {
        'common.grade': {
            'Meta': {'ordering': "('order', 'id')", 'object_name': 'Grade'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10', 'db_index': 'True'}),
            'end_age': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'grade_sublevel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['common.GradeSubLevel']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'start_age': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'common.gradelevel': {
            'Meta': {'ordering': "('id',)", 'object_name': 'GradeLevel'},
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'end_age': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'}),
            'start_age': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'common.gradesublevel': {
            'Meta': {'ordering': "('id',)", 'object_name': 'GradeSubLevel'},
            'end_age': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'grade_level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['common.GradeLevel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'}),
            'start_age': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'common.studentlevel': {
            'Meta': {'ordering': "('id',)", 'object_name': 'StudentLevel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['common']
