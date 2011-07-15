# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Lesson'
        db.create_table('lessons_lesson', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'', max_length=200)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from=None, db_index=True)),
            ('summary', self.gf('django.db.models.fields.TextField')(default=u'')),
            ('goals', self.gf('common.fields.SeparatedValuesField')(default=[])),
        ))
        db.send_create_signal('lessons', ['Lesson'])

        # Adding M2M table for field student_levels on 'Lesson'
        db.create_table('lessons_lesson_student_levels', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('lesson', models.ForeignKey(orm['lessons.lesson'], null=False)),
            ('studentlevel', models.ForeignKey(orm['common.studentlevel'], null=False))
        ))
        db.create_unique('lessons_lesson_student_levels', ['lesson_id', 'studentlevel_id'])

        # Adding M2M table for field subjects on 'Lesson'
        db.create_table('lessons_lesson_subjects', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('lesson', models.ForeignKey(orm['lessons.lesson'], null=False)),
            ('generalsubject', models.ForeignKey(orm['common.generalsubject'], null=False))
        ))
        db.create_unique('lessons_lesson_subjects', ['lesson_id', 'generalsubject_id'])


    def backwards(self, orm):
        
        # Deleting model 'Lesson'
        db.delete_table('lessons_lesson')

        # Removing M2M table for field student_levels on 'Lesson'
        db.delete_table('lessons_lesson_student_levels')

        # Removing M2M table for field subjects on 'Lesson'
        db.delete_table('lessons_lesson_subjects')


    models = {
        'common.generalsubject': {
            'Meta': {'ordering': "('id',)", 'object_name': 'GeneralSubject'},
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'common.studentlevel': {
            'Meta': {'ordering': "('id',)", 'object_name': 'StudentLevel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'lessons.lesson': {
            'Meta': {'object_name': 'Lesson'},
            'goals': ('common.fields.SeparatedValuesField', [], {'default': '[]'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None', 'db_index': 'True'}),
            'student_levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['common.StudentLevel']", 'symmetrical': 'False'}),
            'subjects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['common.GeneralSubject']", 'symmetrical': 'False'}),
            'summary': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200'})
        }
    }

    complete_apps = ['lessons']
