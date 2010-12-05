# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Institution.slug'
        db.alter_column('materials_institution', 'slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=300, populate_from=None, unique_with=()))

        # Changing field 'CommunityTopic.slug'
        db.alter_column('materials_communitytopic', 'slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=100, populate_from=None, unique_with=()))

        # Changing field 'Course.slug'
        db.alter_column('materials_course', 'slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=500, populate_from=None, unique_with=()))

        # Changing field 'MediaFormat.slug'
        db.alter_column('materials_mediaformat', 'slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=100, populate_from=None, unique_with=()))

        # Changing field 'LibraryMaterialType.slug'
        db.alter_column('materials_librarymaterialtype', 'slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=100, populate_from=None, unique_with=()))

        # Changing field 'Collection.slug'
        db.alter_column('materials_collection', 'slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=300, populate_from=None, unique_with=()))

        # Changing field 'CommunityType.slug'
        db.alter_column('materials_communitytype', 'slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=100, populate_from=None, unique_with=()))

        # Changing field 'GeographicRelevance.slug'
        db.alter_column('materials_geographicrelevance', 'slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=100, populate_from=None, unique_with=()))

        # Changing field 'CourseMaterialType.slug'
        db.alter_column('materials_coursematerialtype', 'slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=100, populate_from=None, unique_with=()))

        # Changing field 'CommunityItem.slug'
        db.alter_column('materials_communityitem', 'slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=500, populate_from=None, unique_with=()))

        # Changing field 'GeneralSubject.slug'
        db.alter_column('materials_generalsubject', 'slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=100, populate_from=None, unique_with=()))

        # Changing field 'Library.slug'
        db.alter_column('materials_library', 'slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=500, populate_from=None, unique_with=()))

        # Changing field 'GradeLevel.slug'
        db.alter_column('materials_gradelevel', 'slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=100, populate_from=None, unique_with=()))

        # Changing field 'Country.slug'
        db.alter_column('materials_country', 'slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=100, populate_from=None, unique_with=()))

        # Changing field 'Keyword.slug'
        db.alter_column('materials_keyword', 'slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=500, populate_from=None))


    def backwards(self, orm):
        
        # Changing field 'Institution.slug'
        db.alter_column('materials_institution', 'slug', self.gf('autoslug.fields.AutoSlugField')(max_length=50, unique_with=(), unique=True, populate_from=None))

        # Changing field 'CommunityTopic.slug'
        db.alter_column('materials_communitytopic', 'slug', self.gf('autoslug.fields.AutoSlugField')(max_length=50, unique_with=(), unique=True, populate_from=None))

        # Changing field 'Course.slug'
        db.alter_column('materials_course', 'slug', self.gf('autoslug.fields.AutoSlugField')(max_length=50, unique_with=(), unique=True, populate_from=None))

        # Changing field 'MediaFormat.slug'
        db.alter_column('materials_mediaformat', 'slug', self.gf('autoslug.fields.AutoSlugField')(max_length=50, unique_with=(), unique=True, populate_from=None))

        # Changing field 'LibraryMaterialType.slug'
        db.alter_column('materials_librarymaterialtype', 'slug', self.gf('autoslug.fields.AutoSlugField')(max_length=50, unique_with=(), unique=True, populate_from=None))

        # Changing field 'Collection.slug'
        db.alter_column('materials_collection', 'slug', self.gf('autoslug.fields.AutoSlugField')(max_length=50, unique_with=(), unique=True, populate_from=None))

        # Changing field 'CommunityType.slug'
        db.alter_column('materials_communitytype', 'slug', self.gf('autoslug.fields.AutoSlugField')(max_length=50, unique_with=(), unique=True, populate_from=None))

        # Changing field 'GeographicRelevance.slug'
        db.alter_column('materials_geographicrelevance', 'slug', self.gf('autoslug.fields.AutoSlugField')(max_length=50, unique_with=(), unique=True, populate_from=None))

        # Changing field 'CourseMaterialType.slug'
        db.alter_column('materials_coursematerialtype', 'slug', self.gf('autoslug.fields.AutoSlugField')(max_length=50, unique_with=(), unique=True, populate_from=None))

        # Changing field 'CommunityItem.slug'
        db.alter_column('materials_communityitem', 'slug', self.gf('autoslug.fields.AutoSlugField')(max_length=50, unique_with=(), unique=True, populate_from=None))

        # Changing field 'GeneralSubject.slug'
        db.alter_column('materials_generalsubject', 'slug', self.gf('autoslug.fields.AutoSlugField')(max_length=50, unique_with=(), unique=True, populate_from=None))

        # Changing field 'Library.slug'
        db.alter_column('materials_library', 'slug', self.gf('autoslug.fields.AutoSlugField')(max_length=50, unique_with=(), unique=True, populate_from=None))

        # Changing field 'GradeLevel.slug'
        db.alter_column('materials_gradelevel', 'slug', self.gf('autoslug.fields.AutoSlugField')(max_length=50, unique_with=(), unique=True, populate_from=None))

        # Changing field 'Country.slug'
        db.alter_column('materials_country', 'slug', self.gf('autoslug.fields.AutoSlugField')(max_length=50, unique_with=(), unique=True, populate_from=None))

        # Changing field 'Keyword.slug'
        db.alter_column('materials_keyword', 'slug', self.gf('autoslug.fields.AutoSlugField')(max_length=50, unique_with=(), populate_from=None))


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
        'materials.author': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Author'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['materials.Country']", 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.Author']", 'symmetrical': 'False'}),
            'community_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'community_topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.CommunityTopic']", 'symmetrical': 'False'}),
            'community_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.CommunityType']", 'symmetrical': 'False'}),
            'content_creation_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'general_subjects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GeneralSubject']", 'symmetrical': 'False'}),
            'geographic_relevance': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GeographicRelevance']", 'symmetrical': 'False'}),
            'grade_levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GradeLevel']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_rss': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keywords': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.Keyword']", 'symmetrical': 'False'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.Language']", 'symmetrical': 'False'}),
            'license': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['materials.License']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'news_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'published_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'rss_description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'rss_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
        'materials.country': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Country'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'materials.course': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'Course'},
            'abstract': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.Author']", 'symmetrical': 'False'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['materials.Collection']", 'null': 'True', 'blank': 'True'}),
            'content_creation_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'course_id': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '300', 'blank': 'True'}),
            'course_or_module': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '50', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'curriculum_standards': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'general_subjects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GeneralSubject']", 'symmetrical': 'False'}),
            'geographic_relevance': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GeographicRelevance']", 'symmetrical': 'False'}),
            'grade_levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GradeLevel']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_rss': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['materials.Institution']", 'null': 'True', 'blank': 'True'}),
            'keywords': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.Keyword']", 'symmetrical': 'False'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.Language']", 'symmetrical': 'False'}),
            'license': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['materials.License']"}),
            'material_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.CourseMaterialType']", 'symmetrical': 'False'}),
            'media_formats': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.MediaFormat']", 'symmetrical': 'False'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'ocw': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'provider_id': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '300', 'blank': 'True'}),
            'published_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'related_materials': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.RelatedMaterial']", 'symmetrical': 'False'}),
            'rss_description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'rss_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
        'materials.generalsubject': {
            'Meta': {'ordering': "('id',)", 'object_name': 'GeneralSubject'},
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
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
        'materials.language': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Language'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '3', 'db_index': 'True'})
        },
        'materials.library': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'Library'},
            'abstract': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.Author']", 'symmetrical': 'False'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['materials.Collection']", 'null': 'True', 'blank': 'True'}),
            'content_creation_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'curriculum_standards': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'general_subjects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GeneralSubject']", 'symmetrical': 'False'}),
            'geographic_relevance': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GeographicRelevance']", 'symmetrical': 'False'}),
            'grade_levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GradeLevel']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_rss': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['materials.Institution']", 'null': 'True', 'blank': 'True'}),
            'is_homepage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keywords': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.Keyword']", 'symmetrical': 'False'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.Language']", 'symmetrical': 'False'}),
            'license': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['materials.License']"}),
            'material_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.LibraryMaterialType']", 'symmetrical': 'False'}),
            'media_formats': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.MediaFormat']", 'symmetrical': 'False'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'provider_id': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '300', 'blank': 'True'}),
            'published_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'rss_description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'rss_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
            'bucket': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '50', 'blank': 'True'}),
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
        'materials.relatedmaterial': {
            'Meta': {'ordering': "('title',)", 'object_name': 'RelatedMaterial'},
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'relationship_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "u''", 'max_length': '300', 'blank': 'True'})
        },
        'tags.tag': {
            'Meta': {'object_name': 'Tag'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '100'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['materials']
