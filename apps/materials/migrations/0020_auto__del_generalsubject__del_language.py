# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'GeneralSubject'
        db.delete_table('materials_generalsubject')

        # Deleting model 'Language'
        db.delete_table('materials_language')


    def backwards(self, orm):
        
        # Adding model 'GeneralSubject'
        db.create_table('materials_generalsubject', (
            ('slug', self.gf('autoslug.fields.AutoSlugField')(max_length=100, unique_with=(), unique=True, populate_from=None, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, unique=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('materials', ['GeneralSubject'])

        # Adding model 'Language'
        db.create_table('materials_language', (
            ('order', self.gf('django.db.models.fields.IntegerField')(default=999)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=3, unique=True, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, unique=True)),
        ))
        db.send_create_signal('materials', ['Language'])


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
        'common.generalsubject': {
            'Meta': {'ordering': "('id',)", 'object_name': 'GeneralSubject'},
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'common.language': {
            'Meta': {'ordering': "('order', 'name')", 'object_name': 'Language'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '999'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '3', 'db_index': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'geo.country': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'materials.author': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Author'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Country']", 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "u''", 'max_length': '500', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'materials.collection': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Collection'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '300', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'materials.communityitem': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'CommunityItem'},
            'abstract': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'authors': ('materials.models.common.AutoCreateManyToManyField', [], {'to': "orm['materials.Author']", 'symmetrical': 'False'}),
            'community_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'community_topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.CommunityTopic']", 'symmetrical': 'False'}),
            'community_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.CommunityType']", 'symmetrical': 'False'}),
            'content_creation_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'featured_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'general_subjects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['common.GeneralSubject']", 'symmetrical': 'False'}),
            'geographic_relevance': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GeographicRelevance']", 'symmetrical': 'False'}),
            'grade_levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GradeLevel']", 'symmetrical': 'False'}),
            'http_status': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_rss': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keywords': ('materials.models.common.AutoCreateManyToManyField', [], {'to': "orm['materials.Keyword']", 'symmetrical': 'False'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['common.Language']", 'symmetrical': 'False'}),
            'license': ('materials.models.common.AutoCreateForeignKey', [], {'to': "orm['materials.License']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'news_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'published_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'rss_description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'rss_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'screenshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '500', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'}),
            'tech_requirements': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '300'}),
            'workflow_state': ('django.db.models.fields.CharField', [], {'default': "u'private'", 'max_length': '50'})
        },
        'materials.communitytopic': {
            'Meta': {'ordering': "('id',)", 'object_name': 'CommunityTopic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'materials.communitytype': {
            'Meta': {'ordering': "('id',)", 'object_name': 'CommunityType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'materials.course': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'Course'},
            'abstract': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'authors': ('materials.models.common.AutoCreateManyToManyField', [], {'to': "orm['materials.Author']", 'symmetrical': 'False'}),
            'collection': ('materials.models.common.AutoCreateForeignKey', [], {'to': "orm['materials.Collection']", 'null': 'True', 'blank': 'True'}),
            'content_creation_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'course_id': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '300', 'blank': 'True'}),
            'course_or_module': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'curriculum_standards': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'derived_from': ('materials.models.common.AutoCreateForeignKey', [], {'blank': 'True', 'related_name': "'derived'", 'null': 'True', 'to': "orm['materials.RelatedMaterial']"}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'featured_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'general_subjects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['common.GeneralSubject']", 'symmetrical': 'False'}),
            'geographic_relevance': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GeographicRelevance']", 'symmetrical': 'False'}),
            'grade_levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GradeLevel']", 'symmetrical': 'False'}),
            'http_status': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_rss': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'institution': ('materials.models.common.AutoCreateForeignKey', [], {'to': "orm['materials.Institution']", 'null': 'True', 'blank': 'True'}),
            'keywords': ('materials.models.common.AutoCreateManyToManyField', [], {'to': "orm['materials.Keyword']", 'symmetrical': 'False'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['common.Language']", 'symmetrical': 'False'}),
            'license': ('materials.models.common.AutoCreateForeignKey', [], {'to': "orm['materials.License']"}),
            'material_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.CourseMaterialType']", 'symmetrical': 'False'}),
            'media_formats': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.MediaFormat']", 'symmetrical': 'False'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'postrequisite_1': ('materials.models.common.AutoCreateForeignKey', [], {'blank': 'True', 'related_name': "'postrequisites_1'", 'null': 'True', 'to': "orm['materials.RelatedMaterial']"}),
            'postrequisite_2': ('materials.models.common.AutoCreateForeignKey', [], {'blank': 'True', 'related_name': "'postrequisites_2'", 'null': 'True', 'to': "orm['materials.RelatedMaterial']"}),
            'prerequisite_1': ('materials.models.common.AutoCreateForeignKey', [], {'blank': 'True', 'related_name': "'prerequisites_1'", 'null': 'True', 'to': "orm['materials.RelatedMaterial']"}),
            'prerequisite_2': ('materials.models.common.AutoCreateForeignKey', [], {'blank': 'True', 'related_name': "'prerequisites_2'", 'null': 'True', 'to': "orm['materials.RelatedMaterial']"}),
            'provider_id': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '300', 'blank': 'True'}),
            'published_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'rss_description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'rss_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'screenshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '500', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'}),
            'tech_requirements': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '300'}),
            'workflow_state': ('django.db.models.fields.CharField', [], {'default': "u'private'", 'max_length': '50'})
        },
        'materials.coursematerialtype': {
            'Meta': {'ordering': "('id',)", 'object_name': 'CourseMaterialType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'materials.geographicrelevance': {
            'Meta': {'ordering': "('id',)", 'object_name': 'GeographicRelevance'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'materials.gradelevel': {
            'Meta': {'ordering': "('id',)", 'object_name': 'GradeLevel'},
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'materials.institution': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Institution'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '300', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'materials.keyword': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Keyword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '500'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '500', 'populate_from': 'None', 'db_index': 'True'}),
            'suggested': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'materials.library': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'Library'},
            'abstract': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'authors': ('materials.models.common.AutoCreateManyToManyField', [], {'to': "orm['materials.Author']", 'symmetrical': 'False'}),
            'collection': ('materials.models.common.AutoCreateForeignKey', [], {'to': "orm['materials.Collection']", 'null': 'True', 'blank': 'True'}),
            'content_creation_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'curriculum_standards': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'featured_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'general_subjects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['common.GeneralSubject']", 'symmetrical': 'False'}),
            'geographic_relevance': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GeographicRelevance']", 'symmetrical': 'False'}),
            'grade_levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GradeLevel']", 'symmetrical': 'False'}),
            'http_status': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_rss': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'institution': ('materials.models.common.AutoCreateForeignKey', [], {'to': "orm['materials.Institution']", 'null': 'True', 'blank': 'True'}),
            'is_homepage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keywords': ('materials.models.common.AutoCreateManyToManyField', [], {'to': "orm['materials.Keyword']", 'symmetrical': 'False'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['common.Language']", 'symmetrical': 'False'}),
            'license': ('materials.models.common.AutoCreateForeignKey', [], {'to': "orm['materials.License']"}),
            'material_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.LibraryMaterialType']", 'symmetrical': 'False'}),
            'media_formats': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.MediaFormat']", 'symmetrical': 'False'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'provider_id': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '300', 'blank': 'True'}),
            'published_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'rss_description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'rss_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'screenshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '500', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'}),
            'tech_requirements': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '300'}),
            'workflow_state': ('django.db.models.fields.CharField', [], {'default': "u'private'", 'max_length': '50'})
        },
        'materials.librarymaterialtype': {
            'Meta': {'ordering': "('id',)", 'object_name': 'LibraryMaterialType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'materials.license': {
            'Meta': {'ordering': "('id',)", 'object_name': 'License'},
            'copyright_holder': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '2000', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_url': ('django.db.models.fields.URLField', [], {'default': "u''", 'max_length': '300', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '300'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "u''", 'max_length': '300', 'blank': 'True'})
        },
        'materials.mediaformat': {
            'Meta': {'ordering': "('id',)", 'object_name': 'MediaFormat'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'materials.microsite': {
            'Meta': {'object_name': 'Microsite'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('materials.models.common.AutoCreateManyToManyField', [], {'to': "orm['materials.Keyword']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '100', 'populate_from': 'None', 'db_index': 'True'})
        },
        'materials.relatedmaterial': {
            'Meta': {'ordering': "('title',)", 'object_name': 'RelatedMaterial'},
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "u''", 'max_length': '300', 'blank': 'True'})
        },
        'materials.topic': {
            'Meta': {'ordering': "['microsite', 'tree_id', 'lft']", 'unique_together': "(('name', 'microsite'),)", 'object_name': 'Topic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('materials.models.common.AutoCreateManyToManyField', [], {'symmetrical': 'False', 'to': "orm['materials.Keyword']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'microsite': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'topics'", 'to': "orm['materials.Microsite']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['materials.Topic']", 'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '100', 'populate_from': 'None', 'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'rating.rating': {
            'Meta': {'object_name': 'Rating'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'value': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        'reviews.review': {
            'Meta': {'object_name': 'Review'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'saveditems.saveditem': {
            'Meta': {'object_name': 'SavedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'tags.tag': {
            'Meta': {'object_name': 'Tag'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '100'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None', 'db_index': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['materials']
