# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Evaluation'
        db.create_table('rubrics_evaluation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('ip', self.gf('django.db.models.fields.CharField')(default=u'', max_length=39, blank=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(default=u'', max_length=100, blank=True)),
        ))
        db.send_create_signal('rubrics', ['Evaluation'])

        # Adding unique constraint on 'Evaluation', fields ['user', 'content_type', 'object_id']
        db.create_unique('rubrics_evaluation', ['user_id', 'content_type_id', 'object_id'])

        # Adding model 'Rubric'
        db.create_table('rubrics_rubric', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('rubrics', ['Rubric'])

        # Adding model 'RubricScoreValue'
        db.create_table('rubrics_rubricscorevalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('rubric', self.gf('django.db.models.fields.related.ForeignKey')(related_name='score_values', to=orm['rubrics.Rubric'])),
        ))
        db.send_create_signal('rubrics', ['RubricScoreValue'])

        # Adding unique constraint on 'RubricScoreValue', fields ['rubric', 'value']
        db.create_unique('rubrics_rubricscorevalue', ['rubric_id', 'value'])

        # Adding model 'RubricScore'
        db.create_table('rubrics_rubricscore', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('evaluation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rubrics.Evaluation'])),
            ('score', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rubrics.RubricScoreValue'])),
            ('rubric', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rubrics.Rubric'])),
        ))
        db.send_create_signal('rubrics', ['RubricScore'])

        # Adding unique constraint on 'RubricScore', fields ['evaluation', 'rubric']
        db.create_unique('rubrics_rubricscore', ['evaluation_id', 'rubric_id'])

        # Adding model 'StandardAlignmentScoreValue'
        db.create_table('rubrics_standardalignmentscorevalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('rubrics', ['StandardAlignmentScoreValue'])

        # Adding model 'StandardAlignmentScore'
        db.create_table('rubrics_standardalignmentscore', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('evaluation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rubrics.Evaluation'])),
            ('score', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rubrics.StandardAlignmentScoreValue'])),
            ('alignment_tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['curriculum.AlignmentTag'])),
        ))
        db.send_create_signal('rubrics', ['StandardAlignmentScore'])

        # Adding unique constraint on 'StandardAlignmentScore', fields ['evaluation', 'alignment_tag']
        db.create_unique('rubrics_standardalignmentscore', ['evaluation_id', 'alignment_tag_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'StandardAlignmentScore', fields ['evaluation', 'alignment_tag']
        db.delete_unique('rubrics_standardalignmentscore', ['evaluation_id', 'alignment_tag_id'])

        # Removing unique constraint on 'RubricScore', fields ['evaluation', 'rubric']
        db.delete_unique('rubrics_rubricscore', ['evaluation_id', 'rubric_id'])

        # Removing unique constraint on 'RubricScoreValue', fields ['rubric', 'value']
        db.delete_unique('rubrics_rubricscorevalue', ['rubric_id', 'value'])

        # Removing unique constraint on 'Evaluation', fields ['user', 'content_type', 'object_id']
        db.delete_unique('rubrics_evaluation', ['user_id', 'content_type_id', 'object_id'])

        # Deleting model 'Evaluation'
        db.delete_table('rubrics_evaluation')

        # Deleting model 'Rubric'
        db.delete_table('rubrics_rubric')

        # Deleting model 'RubricScoreValue'
        db.delete_table('rubrics_rubricscorevalue')

        # Deleting model 'RubricScore'
        db.delete_table('rubrics_rubricscore')

        # Deleting model 'StandardAlignmentScoreValue'
        db.delete_table('rubrics_standardalignmentscorevalue')

        # Deleting model 'StandardAlignmentScore'
        db.delete_table('rubrics_standardalignmentscore')


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
        'rubrics.evaluation': {
            'Meta': {'unique_together': "(['user', 'content_type', 'object_id'],)", 'object_name': 'Evaluation'},
            'comment': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'hostname': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '39', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'rubrics.rubric': {
            'Meta': {'ordering': "['id']", 'object_name': 'Rubric'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'rubrics.rubricscore': {
            'Meta': {'unique_together': "(['evaluation', 'rubric'],)", 'object_name': 'RubricScore'},
            'evaluation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rubrics.Evaluation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rubric': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rubrics.Rubric']"}),
            'score': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rubrics.RubricScoreValue']"})
        },
        'rubrics.rubricscorevalue': {
            'Meta': {'ordering': "['id']", 'unique_together': "(['rubric', 'value'],)", 'object_name': 'RubricScoreValue'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rubric': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'score_values'", 'to': "orm['rubrics.Rubric']"}),
            'value': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'rubrics.standardalignmentscore': {
            'Meta': {'unique_together': "(['evaluation', 'alignment_tag'],)", 'object_name': 'StandardAlignmentScore'},
            'alignment_tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['curriculum.AlignmentTag']"}),
            'evaluation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rubrics.Evaluation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rubrics.StandardAlignmentScoreValue']"})
        },
        'rubrics.standardalignmentscorevalue': {
            'Meta': {'ordering': "['id']", 'object_name': 'StandardAlignmentScoreValue'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['rubrics']
