# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'License'
        db.create_table('materials_license', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(default=u'', max_length=300, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default=u'', max_length=300)),
            ('image_url', self.gf('django.db.models.fields.URLField')(default=u'', max_length=300, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('copyright_holder', self.gf('django.db.models.fields.CharField')(default=u'', max_length=2000, blank=True)),
        ))
        db.send_create_signal('materials', ['License'])

        # Adding model 'Author'
        db.create_table('materials_author', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('email', self.gf('django.db.models.fields.EmailField')(default=u'', max_length=500, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Country'], null=True, blank=True)),
        ))
        db.send_create_signal('materials', ['Author'])

        # Adding model 'Keyword'
        db.create_table('materials_keyword', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=500)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=500, populate_from=None, db_index=True)),
            ('suggested', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('materials', ['Keyword'])

        # Adding model 'GeneralSubject'
        db.create_table('materials_generalsubject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=100, populate_from=None, unique_with=(), db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
        ))
        db.send_create_signal('materials', ['GeneralSubject'])

        # Adding model 'GradeLevel'
        db.create_table('materials_gradelevel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=100, populate_from=None, unique_with=(), db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
        ))
        db.send_create_signal('materials', ['GradeLevel'])

        # Adding model 'Language'
        db.create_table('materials_language', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=3, db_index=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=999)),
        ))
        db.send_create_signal('materials', ['Language'])

        # Adding model 'Collection'
        db.create_table('materials_collection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=300)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=300, populate_from=None, unique_with=(), db_index=True)),
            ('disable_alignment_evaluation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('materials', ['Collection'])

        # Adding model 'Institution'
        db.create_table('materials_institution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=300)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=300, populate_from=None, unique_with=(), db_index=True)),
        ))
        db.send_create_signal('materials', ['Institution'])

        # Adding model 'MediaFormat'
        db.create_table('materials_mediaformat', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=100, populate_from=None, unique_with=(), db_index=True)),
        ))
        db.send_create_signal('materials', ['MediaFormat'])

        # Adding model 'GeographicRelevance'
        db.create_table('materials_geographicrelevance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=100, populate_from=None, unique_with=(), db_index=True)),
        ))
        db.send_create_signal('materials', ['GeographicRelevance'])

        # Adding model 'Microsite'
        db.create_table('materials_microsite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=100, populate_from=None, db_index=True)),
        ))
        db.send_create_signal('materials', ['Microsite'])

        # Adding M2M table for field keywords on 'Microsite'
        db.create_table('materials_microsite_keywords', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('microsite', models.ForeignKey(orm['materials.microsite'], null=False)),
            ('keyword', models.ForeignKey(orm['materials.keyword'], null=False))
        ))
        db.create_unique('materials_microsite_keywords', ['microsite_id', 'keyword_id'])

        # Adding model 'Topic'
        db.create_table('materials_topic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=100, populate_from=None, db_index=True)),
            ('microsite', self.gf('django.db.models.fields.related.ForeignKey')(related_name='topics', to=orm['materials.Microsite'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['materials.Topic'], null=True, blank=True)),
            ('other', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('materials', ['Topic'])

        # Adding unique constraint on 'Topic', fields ['name', 'microsite']
        db.create_unique('materials_topic', ['name', 'microsite_id'])

        # Adding M2M table for field keywords on 'Topic'
        db.create_table('materials_topic_keywords', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('topic', models.ForeignKey(orm['materials.topic'], null=False)),
            ('keyword', models.ForeignKey(orm['materials.keyword'], null=False))
        ))
        db.create_unique('materials_topic_keywords', ['topic_id', 'keyword_id'])

        # Adding model 'GenericMaterial'
        db.create_table('materials_genericmaterial', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=300)),
        ))
        db.send_create_signal('materials', ['GenericMaterial'])

        # Adding model 'CourseMaterialType'
        db.create_table('materials_coursematerialtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=100, populate_from=None, unique_with=(), db_index=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('materials', ['CourseMaterialType'])

        # Adding model 'RelatedMaterial'
        db.create_table('materials_relatedmaterial', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('url', self.gf('django.db.models.fields.URLField')(default=u'', max_length=300, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
        ))
        db.send_create_signal('materials', ['RelatedMaterial'])

        # Adding model 'Course'
        db.create_table('materials_course', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=500, populate_from=None, unique_with=(), db_index=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=300, db_index=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('workflow_state', self.gf('django.db.models.fields.CharField')(default=u'private', max_length=50)),
            ('published_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('license', self.gf('materials.models.common.AutoCreateForeignKey')(to=orm['materials.License'])),
            ('in_rss', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('rss_description', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('rss_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('featured_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('url_fetched_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('http_status', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('screenshot', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('course_id', self.gf('django.db.models.fields.CharField')(default=u'', max_length=300, blank=True)),
            ('provider_id', self.gf('django.db.models.fields.CharField')(default=u'', max_length=300, blank=True)),
            ('abstract', self.gf('django.db.models.fields.TextField')(default=u'')),
            ('content_creation_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('tech_requirements', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('institution', self.gf('materials.models.common.AutoCreateForeignKey')(to=orm['materials.Institution'], null=True, blank=True)),
            ('collection', self.gf('materials.models.common.AutoCreateForeignKey')(to=orm['materials.Collection'], null=True, blank=True)),
            ('curriculum_standards', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('course_or_module', self.gf('django.db.models.fields.CharField')(default=u'', max_length=50, blank=True)),
            ('prerequisite_1', self.gf('materials.models.common.AutoCreateForeignKey')(blank=True, related_name='prerequisites_1', null=True, to=orm['materials.RelatedMaterial'])),
            ('prerequisite_2', self.gf('materials.models.common.AutoCreateForeignKey')(blank=True, related_name='prerequisites_2', null=True, to=orm['materials.RelatedMaterial'])),
            ('postrequisite_1', self.gf('materials.models.common.AutoCreateForeignKey')(blank=True, related_name='postrequisites_1', null=True, to=orm['materials.RelatedMaterial'])),
            ('postrequisite_2', self.gf('materials.models.common.AutoCreateForeignKey')(blank=True, related_name='postrequisites_2', null=True, to=orm['materials.RelatedMaterial'])),
            ('derived_from', self.gf('materials.models.common.AutoCreateForeignKey')(blank=True, related_name='derived', null=True, to=orm['materials.RelatedMaterial'])),
            ('new_subject', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('new_level', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('audience', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('materials', ['Course'])

        # Adding M2M table for field authors on 'Course'
        db.create_table('materials_course_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm['materials.course'], null=False)),
            ('author', models.ForeignKey(orm['materials.author'], null=False))
        ))
        db.create_unique('materials_course_authors', ['course_id', 'author_id'])

        # Adding M2M table for field keywords on 'Course'
        db.create_table('materials_course_keywords', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm['materials.course'], null=False)),
            ('keyword', models.ForeignKey(orm['materials.keyword'], null=False))
        ))
        db.create_unique('materials_course_keywords', ['course_id', 'keyword_id'])

        # Adding M2M table for field general_subjects on 'Course'
        db.create_table('materials_course_general_subjects', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm['materials.course'], null=False)),
            ('generalsubject', models.ForeignKey(orm['materials.generalsubject'], null=False))
        ))
        db.create_unique('materials_course_general_subjects', ['course_id', 'generalsubject_id'])

        # Adding M2M table for field grade_levels on 'Course'
        db.create_table('materials_course_grade_levels', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm['materials.course'], null=False)),
            ('gradelevel', models.ForeignKey(orm['materials.gradelevel'], null=False))
        ))
        db.create_unique('materials_course_grade_levels', ['course_id', 'gradelevel_id'])

        # Adding M2M table for field languages on 'Course'
        db.create_table('materials_course_languages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm['materials.course'], null=False)),
            ('language', models.ForeignKey(orm['materials.language'], null=False))
        ))
        db.create_unique('materials_course_languages', ['course_id', 'language_id'])

        # Adding M2M table for field geographic_relevance on 'Course'
        db.create_table('materials_course_geographic_relevance', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm['materials.course'], null=False)),
            ('geographicrelevance', models.ForeignKey(orm['materials.geographicrelevance'], null=False))
        ))
        db.create_unique('materials_course_geographic_relevance', ['course_id', 'geographicrelevance_id'])

        # Adding M2M table for field material_types on 'Course'
        db.create_table('materials_course_material_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm['materials.course'], null=False)),
            ('coursematerialtype', models.ForeignKey(orm['materials.coursematerialtype'], null=False))
        ))
        db.create_unique('materials_course_material_types', ['course_id', 'coursematerialtype_id'])

        # Adding M2M table for field media_formats on 'Course'
        db.create_table('materials_course_media_formats', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm['materials.course'], null=False)),
            ('mediaformat', models.ForeignKey(orm['materials.mediaformat'], null=False))
        ))
        db.create_unique('materials_course_media_formats', ['course_id', 'mediaformat_id'])

        # Adding model 'LibraryMaterialType'
        db.create_table('materials_librarymaterialtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=100, populate_from=None, unique_with=(), db_index=True)),
        ))
        db.send_create_signal('materials', ['LibraryMaterialType'])

        # Adding model 'Library'
        db.create_table('materials_library', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=500, populate_from=None, unique_with=(), db_index=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=300, db_index=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('workflow_state', self.gf('django.db.models.fields.CharField')(default=u'private', max_length=50)),
            ('published_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('license', self.gf('materials.models.common.AutoCreateForeignKey')(to=orm['materials.License'])),
            ('in_rss', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('rss_description', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('rss_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('featured_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('url_fetched_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('http_status', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('screenshot', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('provider_id', self.gf('django.db.models.fields.CharField')(default=u'', max_length=300, blank=True)),
            ('abstract', self.gf('django.db.models.fields.TextField')(default=u'')),
            ('content_creation_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('tech_requirements', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('institution', self.gf('materials.models.common.AutoCreateForeignKey')(to=orm['materials.Institution'], null=True, blank=True)),
            ('collection', self.gf('materials.models.common.AutoCreateForeignKey')(to=orm['materials.Collection'], null=True, blank=True)),
            ('curriculum_standards', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('is_homepage', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('new_subject', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('new_level', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('audience', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('materials', ['Library'])

        # Adding M2M table for field authors on 'Library'
        db.create_table('materials_library_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('library', models.ForeignKey(orm['materials.library'], null=False)),
            ('author', models.ForeignKey(orm['materials.author'], null=False))
        ))
        db.create_unique('materials_library_authors', ['library_id', 'author_id'])

        # Adding M2M table for field keywords on 'Library'
        db.create_table('materials_library_keywords', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('library', models.ForeignKey(orm['materials.library'], null=False)),
            ('keyword', models.ForeignKey(orm['materials.keyword'], null=False))
        ))
        db.create_unique('materials_library_keywords', ['library_id', 'keyword_id'])

        # Adding M2M table for field general_subjects on 'Library'
        db.create_table('materials_library_general_subjects', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('library', models.ForeignKey(orm['materials.library'], null=False)),
            ('generalsubject', models.ForeignKey(orm['materials.generalsubject'], null=False))
        ))
        db.create_unique('materials_library_general_subjects', ['library_id', 'generalsubject_id'])

        # Adding M2M table for field grade_levels on 'Library'
        db.create_table('materials_library_grade_levels', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('library', models.ForeignKey(orm['materials.library'], null=False)),
            ('gradelevel', models.ForeignKey(orm['materials.gradelevel'], null=False))
        ))
        db.create_unique('materials_library_grade_levels', ['library_id', 'gradelevel_id'])

        # Adding M2M table for field languages on 'Library'
        db.create_table('materials_library_languages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('library', models.ForeignKey(orm['materials.library'], null=False)),
            ('language', models.ForeignKey(orm['materials.language'], null=False))
        ))
        db.create_unique('materials_library_languages', ['library_id', 'language_id'])

        # Adding M2M table for field geographic_relevance on 'Library'
        db.create_table('materials_library_geographic_relevance', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('library', models.ForeignKey(orm['materials.library'], null=False)),
            ('geographicrelevance', models.ForeignKey(orm['materials.geographicrelevance'], null=False))
        ))
        db.create_unique('materials_library_geographic_relevance', ['library_id', 'geographicrelevance_id'])

        # Adding M2M table for field material_types on 'Library'
        db.create_table('materials_library_material_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('library', models.ForeignKey(orm['materials.library'], null=False)),
            ('librarymaterialtype', models.ForeignKey(orm['materials.librarymaterialtype'], null=False))
        ))
        db.create_unique('materials_library_material_types', ['library_id', 'librarymaterialtype_id'])

        # Adding M2M table for field media_formats on 'Library'
        db.create_table('materials_library_media_formats', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('library', models.ForeignKey(orm['materials.library'], null=False)),
            ('mediaformat', models.ForeignKey(orm['materials.mediaformat'], null=False))
        ))
        db.create_unique('materials_library_media_formats', ['library_id', 'mediaformat_id'])

        # Adding model 'CommunityType'
        db.create_table('materials_communitytype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=100, populate_from=None, unique_with=(), db_index=True)),
        ))
        db.send_create_signal('materials', ['CommunityType'])

        # Adding model 'CommunityTopic'
        db.create_table('materials_communitytopic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=100, populate_from=None, unique_with=(), db_index=True)),
        ))
        db.send_create_signal('materials', ['CommunityTopic'])

        # Adding model 'CommunityItem'
        db.create_table('materials_communityitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=500, populate_from=None, unique_with=(), db_index=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=300, db_index=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('workflow_state', self.gf('django.db.models.fields.CharField')(default=u'private', max_length=50)),
            ('published_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('license', self.gf('materials.models.common.AutoCreateForeignKey')(to=orm['materials.License'])),
            ('in_rss', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('rss_description', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('rss_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('featured_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('url_fetched_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('http_status', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('screenshot', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('abstract', self.gf('django.db.models.fields.TextField')(default=u'')),
            ('content_creation_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('tech_requirements', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('community_featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('news_featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('new_subject', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('new_level', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('audience', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('materials', ['CommunityItem'])

        # Adding M2M table for field authors on 'CommunityItem'
        db.create_table('materials_communityitem_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('communityitem', models.ForeignKey(orm['materials.communityitem'], null=False)),
            ('author', models.ForeignKey(orm['materials.author'], null=False))
        ))
        db.create_unique('materials_communityitem_authors', ['communityitem_id', 'author_id'])

        # Adding M2M table for field keywords on 'CommunityItem'
        db.create_table('materials_communityitem_keywords', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('communityitem', models.ForeignKey(orm['materials.communityitem'], null=False)),
            ('keyword', models.ForeignKey(orm['materials.keyword'], null=False))
        ))
        db.create_unique('materials_communityitem_keywords', ['communityitem_id', 'keyword_id'])

        # Adding M2M table for field general_subjects on 'CommunityItem'
        db.create_table('materials_communityitem_general_subjects', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('communityitem', models.ForeignKey(orm['materials.communityitem'], null=False)),
            ('generalsubject', models.ForeignKey(orm['materials.generalsubject'], null=False))
        ))
        db.create_unique('materials_communityitem_general_subjects', ['communityitem_id', 'generalsubject_id'])

        # Adding M2M table for field grade_levels on 'CommunityItem'
        db.create_table('materials_communityitem_grade_levels', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('communityitem', models.ForeignKey(orm['materials.communityitem'], null=False)),
            ('gradelevel', models.ForeignKey(orm['materials.gradelevel'], null=False))
        ))
        db.create_unique('materials_communityitem_grade_levels', ['communityitem_id', 'gradelevel_id'])

        # Adding M2M table for field languages on 'CommunityItem'
        db.create_table('materials_communityitem_languages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('communityitem', models.ForeignKey(orm['materials.communityitem'], null=False)),
            ('language', models.ForeignKey(orm['materials.language'], null=False))
        ))
        db.create_unique('materials_communityitem_languages', ['communityitem_id', 'language_id'])

        # Adding M2M table for field geographic_relevance on 'CommunityItem'
        db.create_table('materials_communityitem_geographic_relevance', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('communityitem', models.ForeignKey(orm['materials.communityitem'], null=False)),
            ('geographicrelevance', models.ForeignKey(orm['materials.geographicrelevance'], null=False))
        ))
        db.create_unique('materials_communityitem_geographic_relevance', ['communityitem_id', 'geographicrelevance_id'])

        # Adding M2M table for field community_types on 'CommunityItem'
        db.create_table('materials_communityitem_community_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('communityitem', models.ForeignKey(orm['materials.communityitem'], null=False)),
            ('communitytype', models.ForeignKey(orm['materials.communitytype'], null=False))
        ))
        db.create_unique('materials_communityitem_community_types', ['communityitem_id', 'communitytype_id'])

        # Adding M2M table for field community_topics on 'CommunityItem'
        db.create_table('materials_communityitem_community_topics', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('communityitem', models.ForeignKey(orm['materials.communityitem'], null=False)),
            ('communitytopic', models.ForeignKey(orm['materials.communitytopic'], null=False))
        ))
        db.create_unique('materials_communityitem_community_topics', ['communityitem_id', 'communitytopic_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Topic', fields ['name', 'microsite']
        db.delete_unique('materials_topic', ['name', 'microsite_id'])

        # Deleting model 'License'
        db.delete_table('materials_license')

        # Deleting model 'Author'
        db.delete_table('materials_author')

        # Deleting model 'Keyword'
        db.delete_table('materials_keyword')

        # Deleting model 'GeneralSubject'
        db.delete_table('materials_generalsubject')

        # Deleting model 'GradeLevel'
        db.delete_table('materials_gradelevel')

        # Deleting model 'Language'
        db.delete_table('materials_language')

        # Deleting model 'Collection'
        db.delete_table('materials_collection')

        # Deleting model 'Institution'
        db.delete_table('materials_institution')

        # Deleting model 'MediaFormat'
        db.delete_table('materials_mediaformat')

        # Deleting model 'GeographicRelevance'
        db.delete_table('materials_geographicrelevance')

        # Deleting model 'Microsite'
        db.delete_table('materials_microsite')

        # Removing M2M table for field keywords on 'Microsite'
        db.delete_table('materials_microsite_keywords')

        # Deleting model 'Topic'
        db.delete_table('materials_topic')

        # Removing M2M table for field keywords on 'Topic'
        db.delete_table('materials_topic_keywords')

        # Deleting model 'GenericMaterial'
        db.delete_table('materials_genericmaterial')

        # Deleting model 'CourseMaterialType'
        db.delete_table('materials_coursematerialtype')

        # Deleting model 'RelatedMaterial'
        db.delete_table('materials_relatedmaterial')

        # Deleting model 'Course'
        db.delete_table('materials_course')

        # Removing M2M table for field authors on 'Course'
        db.delete_table('materials_course_authors')

        # Removing M2M table for field keywords on 'Course'
        db.delete_table('materials_course_keywords')

        # Removing M2M table for field general_subjects on 'Course'
        db.delete_table('materials_course_general_subjects')

        # Removing M2M table for field grade_levels on 'Course'
        db.delete_table('materials_course_grade_levels')

        # Removing M2M table for field languages on 'Course'
        db.delete_table('materials_course_languages')

        # Removing M2M table for field geographic_relevance on 'Course'
        db.delete_table('materials_course_geographic_relevance')

        # Removing M2M table for field material_types on 'Course'
        db.delete_table('materials_course_material_types')

        # Removing M2M table for field media_formats on 'Course'
        db.delete_table('materials_course_media_formats')

        # Deleting model 'LibraryMaterialType'
        db.delete_table('materials_librarymaterialtype')

        # Deleting model 'Library'
        db.delete_table('materials_library')

        # Removing M2M table for field authors on 'Library'
        db.delete_table('materials_library_authors')

        # Removing M2M table for field keywords on 'Library'
        db.delete_table('materials_library_keywords')

        # Removing M2M table for field general_subjects on 'Library'
        db.delete_table('materials_library_general_subjects')

        # Removing M2M table for field grade_levels on 'Library'
        db.delete_table('materials_library_grade_levels')

        # Removing M2M table for field languages on 'Library'
        db.delete_table('materials_library_languages')

        # Removing M2M table for field geographic_relevance on 'Library'
        db.delete_table('materials_library_geographic_relevance')

        # Removing M2M table for field material_types on 'Library'
        db.delete_table('materials_library_material_types')

        # Removing M2M table for field media_formats on 'Library'
        db.delete_table('materials_library_media_formats')

        # Deleting model 'CommunityType'
        db.delete_table('materials_communitytype')

        # Deleting model 'CommunityTopic'
        db.delete_table('materials_communitytopic')

        # Deleting model 'CommunityItem'
        db.delete_table('materials_communityitem')

        # Removing M2M table for field authors on 'CommunityItem'
        db.delete_table('materials_communityitem_authors')

        # Removing M2M table for field keywords on 'CommunityItem'
        db.delete_table('materials_communityitem_keywords')

        # Removing M2M table for field general_subjects on 'CommunityItem'
        db.delete_table('materials_communityitem_general_subjects')

        # Removing M2M table for field grade_levels on 'CommunityItem'
        db.delete_table('materials_communityitem_grade_levels')

        # Removing M2M table for field languages on 'CommunityItem'
        db.delete_table('materials_communityitem_languages')

        # Removing M2M table for field geographic_relevance on 'CommunityItem'
        db.delete_table('materials_communityitem_geographic_relevance')

        # Removing M2M table for field community_types on 'CommunityItem'
        db.delete_table('materials_communityitem_community_types')

        # Removing M2M table for field community_topics on 'CommunityItem'
        db.delete_table('materials_communityitem_community_topics')


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
            'Meta': {'ordering': "('standard', 'grade', 'category', 'code')", 'unique_together': "(('grade', 'category', 'code'),)", 'object_name': 'AlignmentTag'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['curriculum.LearningObjectiveCategory']"}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'grade': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['curriculum.Grade']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'standard': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['curriculum.Standard']"}),
            'subcategory': ('django.db.models.fields.TextField', [], {})
        },
        'curriculum.grade': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Grade'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10', 'db_index': 'True'}),
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
        'curriculum.taggedmaterial': {
            'Meta': {'unique_together': "(('user', 'tag', 'content_type', 'object_id'),)", 'object_name': 'TaggedMaterial'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['curriculum.AlignmentTag']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
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
            'disable_alignment_evaluation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '300', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'})
        },
        'materials.communityitem': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'CommunityItem'},
            'abstract': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'audience': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'authors': ('materials.models.common.AutoCreateManyToManyField', [], {'to': "orm['materials.Author']", 'symmetrical': 'False'}),
            'community_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'community_topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.CommunityTopic']", 'symmetrical': 'False'}),
            'community_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.CommunityType']", 'symmetrical': 'False'}),
            'content_creation_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'featured_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'general_subjects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GeneralSubject']", 'symmetrical': 'False'}),
            'geographic_relevance': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GeographicRelevance']", 'symmetrical': 'False'}),
            'grade_levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GradeLevel']", 'symmetrical': 'False'}),
            'http_status': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_rss': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keywords': ('materials.models.common.AutoCreateManyToManyField', [], {'to': "orm['materials.Keyword']", 'symmetrical': 'False'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.Language']", 'symmetrical': 'False'}),
            'license': ('materials.models.common.AutoCreateForeignKey', [], {'to': "orm['materials.License']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'new_level': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'new_subject': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'news_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'published_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'rss_description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'rss_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'screenshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '500', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'}),
            'tech_requirements': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '300', 'db_index': 'True'}),
            'url_fetched_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
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
            'audience': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
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
            'general_subjects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GeneralSubject']", 'symmetrical': 'False'}),
            'geographic_relevance': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GeographicRelevance']", 'symmetrical': 'False'}),
            'grade_levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GradeLevel']", 'symmetrical': 'False'}),
            'http_status': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_rss': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'institution': ('materials.models.common.AutoCreateForeignKey', [], {'to': "orm['materials.Institution']", 'null': 'True', 'blank': 'True'}),
            'keywords': ('materials.models.common.AutoCreateManyToManyField', [], {'to': "orm['materials.Keyword']", 'symmetrical': 'False'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.Language']", 'symmetrical': 'False'}),
            'license': ('materials.models.common.AutoCreateForeignKey', [], {'to': "orm['materials.License']"}),
            'material_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.CourseMaterialType']", 'symmetrical': 'False'}),
            'media_formats': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.MediaFormat']", 'symmetrical': 'False'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'new_level': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'new_subject': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
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
            'url': ('django.db.models.fields.URLField', [], {'max_length': '300', 'db_index': 'True'}),
            'url_fetched_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'workflow_state': ('django.db.models.fields.CharField', [], {'default': "u'private'", 'max_length': '50'})
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
        'materials.genericmaterial': {
            'Meta': {'object_name': 'GenericMaterial'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '300'})
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
            'Meta': {'ordering': "('order', 'name')", 'object_name': 'Language'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '999'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '3', 'db_index': 'True'})
        },
        'materials.library': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'Library'},
            'abstract': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'audience': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'authors': ('materials.models.common.AutoCreateManyToManyField', [], {'to': "orm['materials.Author']", 'symmetrical': 'False'}),
            'collection': ('materials.models.common.AutoCreateForeignKey', [], {'to': "orm['materials.Collection']", 'null': 'True', 'blank': 'True'}),
            'content_creation_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'curriculum_standards': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'featured_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'general_subjects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GeneralSubject']", 'symmetrical': 'False'}),
            'geographic_relevance': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GeographicRelevance']", 'symmetrical': 'False'}),
            'grade_levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.GradeLevel']", 'symmetrical': 'False'}),
            'http_status': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_rss': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'institution': ('materials.models.common.AutoCreateForeignKey', [], {'to': "orm['materials.Institution']", 'null': 'True', 'blank': 'True'}),
            'is_homepage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keywords': ('materials.models.common.AutoCreateManyToManyField', [], {'to': "orm['materials.Keyword']", 'symmetrical': 'False'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.Language']", 'symmetrical': 'False'}),
            'license': ('materials.models.common.AutoCreateForeignKey', [], {'to': "orm['materials.License']"}),
            'material_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.LibraryMaterialType']", 'symmetrical': 'False'}),
            'media_formats': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['materials.MediaFormat']", 'symmetrical': 'False'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'new_level': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'new_subject': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'provider_id': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '300', 'blank': 'True'}),
            'published_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'rss_description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'rss_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'screenshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '500', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'}),
            'tech_requirements': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '300', 'db_index': 'True'}),
            'url_fetched_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
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

    complete_apps = ['materials']
