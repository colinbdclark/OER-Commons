# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.db.models import Count


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'VisitCounter'
        db.create_table('visitcounts_visitcounter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('visits', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('visitcounts', ['VisitCounter'])

        # Migrate old data for Visit model to new VisitCounter.
        Visit = orm['visitcounts.Visit']
        VisitCounter = orm['visitcounts.VisitCounter']

        for visit in Visit.objects.values(
            "object_id", "content_type_id"
        ).annotate(visits=Count("id")):
            object_id = visit["object_id"]
            content_type_id = visit["content_type_id"]
            visits = visit["visits"]
            content_type = orm["contenttypes.ContentType"].objects.get(id=content_type_id)

            VisitCounter.objects.create(
                content_type=content_type,
                object_id=object_id,
                visits=visits
            )

    def backwards(self, orm):

        # Deleting model 'VisitCounter'
        db.delete_table('visitcounts_visitcounter')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'visitcounts.visit': {
            'Meta': {'object_name': 'Visit'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'visitcounts.visitcounter': {
            'Meta': {'object_name': 'VisitCounter'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'visits': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['visitcounts']
