# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Document.file'
        db.alter_column('authoring_document', 'file', self.gf('django.db.models.fields.files.FileField')(max_length=500))

        # Changing field 'Image.image'
        db.alter_column('authoring_image', 'image', self.gf('django.db.models.fields.files.ImageField')(max_length=500))


    def backwards(self, orm):
        
        # Changing field 'Document.file'
        db.alter_column('authoring_document', 'file', self.gf('django.db.models.fields.files.ImageField')(max_length=100))

        # Changing field 'Image.image'
        db.alter_column('authoring_image', 'image', self.gf('django.db.models.fields.files.ImageField')(max_length=100))


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
        'authoring.authoredmaterial': {
            'Meta': {'object_name': 'AuthoredMaterial'},
            'abstract': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['auth.User']"}),
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'featured_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'general_subjects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GeneralSubject']", 'symmetrical': 'False'}),
            'grade_levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['common.GradeLevel']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_new': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'keywords': ('core.fields.AutoCreateManyToManyField', [], {'to': "orm['materials.Keyword']", 'symmetrical': 'False'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.Language']", 'symmetrical': 'False'}),
            'learning_goals': ('core.fields.AutoCreateManyToManyField', [], {'to': "orm['authoring.LearningGoal']", 'symmetrical': 'False'}),
            'license': ('core.fields.AutoCreateForeignKey', [], {'to': "orm['materials.License']", 'null': 'True'}),
            'material_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.CourseMaterialType']", 'symmetrical': 'False'}),
            'media_formats': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['common.MediaFormat']", 'symmetrical': 'False'}),
            'modified_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'owners': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'+'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'published_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None', 'db_index': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200'}),
            'workflow_state': ('django.db.models.fields.CharField', [], {'default': "u'private'", 'max_length': '50'})
        },
        'authoring.authoredmaterialdraft': {
            'Meta': {'object_name': 'AuthoredMaterialDraft'},
            'abstract': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'general_subjects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GeneralSubject']", 'symmetrical': 'False'}),
            'grade_levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['common.GradeLevel']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('core.fields.AutoCreateManyToManyField', [], {'to': "orm['materials.Keyword']", 'symmetrical': 'False'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.Language']", 'symmetrical': 'False'}),
            'learning_goals': ('core.fields.AutoCreateManyToManyField', [], {'to': "orm['authoring.LearningGoal']", 'symmetrical': 'False'}),
            'license': ('core.fields.AutoCreateForeignKey', [], {'to': "orm['materials.License']", 'null': 'True'}),
            'material': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'draft'", 'unique': 'True', 'to': "orm['authoring.AuthoredMaterial']"}),
            'material_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.CourseMaterialType']", 'symmetrical': 'False'}),
            'modified_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200'})
        },
        'authoring.document': {
            'Meta': {'object_name': 'Document'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'material': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authoring.AuthoredMaterial']"})
        },
        'authoring.embed': {
            'Meta': {'object_name': 'Embed'},
            'embed_url': ('django.db.models.fields.URLField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thumbnail': ('django.db.models.fields.URLField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'})
        },
        'authoring.image': {
            'Meta': {'object_name': 'Image'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '500'}),
            'material': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authoring.AuthoredMaterial']"})
        },
        'authoring.learninggoal': {
            'Meta': {'object_name': 'LearningGoal'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'common.grade': {
            'Meta': {'ordering': "('order', 'id')", 'object_name': 'Grade'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10', 'db_index': 'True'}),
            'grade_sublevel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['common.GradeSubLevel']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'common.gradelevel': {
            'Meta': {'ordering': "('id',)", 'object_name': 'GradeLevel'},
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'common.gradesublevel': {
            'Meta': {'ordering': "('id',)", 'object_name': 'GradeSubLevel'},
            'grade_level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['common.GradeLevel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'common.mediaformat': {
            'Meta': {'ordering': "('id',)", 'object_name': 'MediaFormat'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'curriculum.alignmenttag': {
            'Meta': {'ordering': "('standard', 'grade', 'category', 'code')", 'unique_together': "(('grade', 'category', 'code'),)", 'object_name': 'AlignmentTag'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['curriculum.LearningObjectiveCategory']"}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_grade': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['common.Grade']"}),
            'grade': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['common.Grade']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'standard': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['curriculum.Standard']"}),
            'subcategory': ('django.db.models.fields.TextField', [], {})
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
        'curriculum.taggedmaterial': {
            'Meta': {'unique_together': "(('user', 'tag', 'content_type', 'object_id'),)", 'object_name': 'TaggedMaterial'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['curriculum.AlignmentTag']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'materials.coursematerialtype': {
            'Meta': {'ordering': "('order', 'id')", 'object_name': 'CourseMaterialType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'materials.generalsubject': {
            'Meta': {'ordering': "('id',)", 'object_name': 'GeneralSubject'},
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '100', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'materials.keyword': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Keyword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '500'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '500', 'populate_from': 'None', 'db_index': 'True'}),
            'suggested': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'materials.language': {
            'Meta': {'ordering': "('order', 'name')", 'object_name': 'Language'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '999'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '3', 'db_index': 'True'})
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
        'rating.rating': {
            'Meta': {'unique_together': "(['content_type', 'object_id', 'user'],)", 'object_name': 'Rating'},
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

    complete_apps = ['authoring']
