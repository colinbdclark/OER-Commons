# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Feed'
        db.create_table('blog_feed', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'', max_length=500, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=500)),
            ('site_url', self.gf('django.db.models.fields.URLField')(default=u'', max_length=500, blank=True)),
        ))
        db.send_create_signal('blog', ['Feed'])

        # Adding model 'Post'
        db.create_table('blog_post', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=1000, populate_from=None, db_index=True)),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['blog.Feed'])),
            ('published_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(default=u'')),
            ('snippet', self.gf('django.db.models.fields.TextField')(default=u'')),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=500)),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('blog', ['Post'])


    def backwards(self, orm):
        
        # Deleting model 'Feed'
        db.delete_table('blog_feed')

        # Deleting model 'Post'
        db.delete_table('blog_post')


    models = {
        'blog.feed': {
            'Meta': {'object_name': 'Feed'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site_url': ('django.db.models.fields.URLField', [], {'default': "u''", 'max_length': '500', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '500', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '500'})
        },
        'blog.post': {
            'Meta': {'ordering': "['published_on']", 'object_name': 'Post'},
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blog.Feed']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'published_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '1000', 'populate_from': 'None', 'db_index': 'True'}),
            'snippet': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'text': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '500'})
        }
    }

    complete_apps = ['blog']
