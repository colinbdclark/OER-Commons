# encoding: utf-8
import datetime
from pyexpat import model
from django.contrib.contenttypes.models import ContentType
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        from haystack_scheduled.indexes import Indexed
        for score in orm.StandardAlignmentScore.objects.all():
            model = ContentType.objects.get(id=score.content_type_id).model_class()
            obj = model.objects.get(pk=score.object_id)
            if isinstance(obj, Indexed):
                obj.reindex()
        for score in orm.RubricScore.objects.all():
            model = ContentType.objects.get(id=score.content_type_id).model_class()
            obj = model.objects.get(pk=score.object_id)
            if isinstance(obj, Indexed):
                obj.reindex()

    def backwards(self, orm):
        "Write your backwards methods here."


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'curriculum.alignmenttag': {
            'Meta': {'ordering': "('standard', 'grade', 'category', 'code')", 'unique_together': "(('standard', 'grade', 'category', 'code'),)", 'object_name': 'AlignmentTag'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['curriculum.LearningObjectiveCategory']"}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '4', 'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'grade': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['curriculum.Grade']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'standard': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['curriculum.Standard']"}),
            'subcategory': ('django.db.models.fields.TextField', [], {})
        },
        'curriculum.grade': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Grade'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '4', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'curriculum.learningobjectivecategory': {
            'Meta': {'ordering': "('id',)", 'object_name': 'LearningObjectiveCategory'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '8', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'curriculum.standard': {
            'Meta': {'ordering': "('id',)", 'unique_together': "(['code', 'substandard_code'],)", 'object_name': 'Standard'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '4', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'substandard_code': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '20', 'db_index': 'True'})
        },
        'rubrics.rubric': {
            'Meta': {'ordering': "['id']", 'object_name': 'Rubric'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'rubrics.rubricscore': {
            'Meta': {'object_name': 'RubricScore'},
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'rubric': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rubrics.Rubric']"}),
            'score': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rubrics.RubricScoreValue']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'rubrics.rubricscorevalue': {
            'Meta': {'ordering': "['rubric', 'id']", 'object_name': 'RubricScoreValue'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rubric': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'score_values'", 'to': "orm['rubrics.Rubric']"}),
            'value': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'rubrics.standardalignmentscore': {
            'Meta': {'object_name': 'StandardAlignmentScore'},
            'alignment_tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['curriculum.AlignmentTag']"}),
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'score': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rubrics.StandardAlignmentScoreValue']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'rubrics.standardalignmentscorevalue': {
            'Meta': {'ordering': "['id']", 'object_name': 'StandardAlignmentScoreValue'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['rubrics']
