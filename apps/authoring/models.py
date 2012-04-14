from annoying.functions import get_object_or_None
from autoslug import AutoSlugField
from common.models import GradeLevel, MediaFormat, GradeSubLevel, Grade
from core.fields import AutoCreateForeignKey, AutoCreateManyToManyField
from curriculum.models import TaggedMaterial
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from materials.models import Keyword, \
    GeneralSubject, License, CourseMaterialType
from materials.models.common import Language
from materials.models.material import TAGGED, REVIEWED, RATED, PUBLISHED_STATE, WORKFLOW_STATES, PRIVATE_STATE
from materials.models.microsite import Microsite, Topic
from pyquery import PyQuery as pq
from rating.models import Rating
from reviews.models import Review
from rubrics.models import Evaluation, EvaluatedItemMixin
from saveditems.models import SavedItem
from tags.models import Tag
from utils.templatetags.utils import full_url
from visitcounts.models import Visit

import gdata.youtube
import gdata.youtube.service
import datetime
import embedly
import os


class LearningGoal(models.Model):

    title = models.CharField(max_length=200)

    def __unicode__(self):
        return self.title


class AbstractAuthoredMaterial(models.Model):

    title = models.CharField(max_length=200, default=u"")
    text = models.TextField(default=u"")

    abstract = models.TextField(default=u"")

    learning_goals = AutoCreateManyToManyField(LearningGoal)
    keywords = AutoCreateManyToManyField(Keyword)
    general_subjects = models.ManyToManyField(GeneralSubject)
    grade_levels = models.ManyToManyField(GradeLevel)
    grade_sublevels = models.ManyToManyField(GradeSubLevel)
    grades = models.ManyToManyField(Grade)
    languages = models.ManyToManyField(Language)
    material_types = models.ManyToManyField(CourseMaterialType)
    license = AutoCreateForeignKey(License, null=True, respect_all_fields=True)

    class Meta:
        abstract = True


class AuthoredMaterialDraft(AbstractAuthoredMaterial):

    material = models.OneToOneField("authoring.AuthoredMaterial", related_name="draft")
    created_timestamp = models.DateTimeField(auto_now_add=True)
    modified_timestamp = models.DateTimeField(auto_now=True)

    @models.permalink
    def get_absolute_url(self):
        return "authoring:preview", [], dict(pk=self.material.pk)


class AuthoredMaterial(AbstractAuthoredMaterial, EvaluatedItemMixin):

    slug = AutoSlugField(populate_from="title", always_update=True)

    owners = models.ManyToManyField(User, related_name="+")
    author = models.ForeignKey(User, related_name="+")

    media_formats = models.ManyToManyField(MediaFormat)

    is_new = models.BooleanField(default=True)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    modified_timestamp = models.DateTimeField(auto_now=True)
    published_on = models.DateTimeField(null=True, blank=True)
    featured = models.BooleanField(default=False, verbose_name=_(u"Featured"))
    featured_on = models.DateTimeField(null=True, blank=True)

    tags = generic.GenericRelation(Tag)
    reviews = generic.GenericRelation(Review)
    saved_items = generic.GenericRelation(SavedItem)
    ratings = generic.GenericRelation(Rating)
    alignment_tags = generic.GenericRelation(TaggedMaterial)

    workflow_state = models.CharField(max_length=50, default=PRIVATE_STATE,
                                      choices=WORKFLOW_STATES)

    screenshot = models.ImageField(null=True, blank=True, upload_to="upload/materials/screenshots")

    http_status = 200

    @property
    def url(self):
        return full_url(self.get_view_full_url())

    def get_draft(self):
        draft = get_object_or_None(AuthoredMaterialDraft, material=self)
        if not draft:
            draft = AuthoredMaterialDraft(material=self)
            for field in AbstractAuthoredMaterial._meta.fields:
                setattr(draft, field.name, getattr(self, field.name))
            draft.save()
            for m2m in AbstractAuthoredMaterial._meta.many_to_many:
                setattr(draft, m2m.name, getattr(self, m2m.name).all())
            draft_content_type = ContentType.objects.get_for_model(draft)
            material_content_type = ContentType.objects.get_for_model(self)
            for tagged in TaggedMaterial.objects.filter(
                content_type=material_content_type,
                object_id=self.id,
                user=self.author,
            ):
                TaggedMaterial.objects.create(
                    content_type=draft_content_type,
                    object_id=draft.id,
                    user=self.author,
                    tag=tagged.tag,
                )
        return draft

    @classmethod
    def publish_draft(cls, draft):
        material = draft.material
        for field in AbstractAuthoredMaterial._meta.fields:
            setattr(material, field.name, getattr(draft, field.name))
        for m2m in AbstractAuthoredMaterial._meta.many_to_many:
            setattr(material, m2m.name, getattr(draft, m2m.name).all())
        material.workflow_state = PUBLISHED_STATE
        material.is_new = False

        # Update alignment tags
        draft_content_type = ContentType.objects.get_for_model(draft)
        material_content_type = ContentType.objects.get_for_model(material)
        TaggedMaterial.objects.filter(
            content_type=material_content_type,
            object_id=material.id,
            user=material.author,
        ).delete()
        for tagged in TaggedMaterial.objects.filter(
            content_type=draft_content_type,
            object_id=draft.id,
        ):
            tagged.content_type = material_content_type
            tagged.object_id = material.id
            tagged.save()

        # Update media formats based on different media types included into material text.
        media_formats = [MediaFormat.objects.get(slug="text-html")]
        document = pq(material.text)
        if document.find("figure.image").length:
            media_formats.append(MediaFormat.objects.get(slug="graphics-photos"))
        if document.find("figure.video").length:
            media_formats.append(MediaFormat.objects.get(slug="video"))
        if document.find("figure.audio").length:
            media_formats.append(MediaFormat.objects.get(slug="audio"))
        if document.find("figure.download").length:
            media_formats.append(MediaFormat.objects.get(slug="downloadable-docs"))
        material.media_formats = media_formats

        material.save()
        draft.delete()
        return material

    def save(self, *args, **kwargs):
        if self.workflow_state == PUBLISHED_STATE and not self.published_on:
            self.published_on = datetime.datetime.now()
        if self.featured and not self.featured_on:
            self.featured_on = datetime.datetime.now()
        if not self.featured:
            self.featured_on = None

        super(AuthoredMaterial, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        kwargs = dict(pk=self.pk)
        if self.slug: kwargs["slug"] = self.slug
        return "authoring:view", [], kwargs

    @models.permalink
    def get_view_full_url(self):
        kwargs = dict(pk=self.pk)
        if self.slug: kwargs["slug"] = self.slug
        return "authoring:view_full", [], kwargs

    @models.permalink
    def get_edit_url(self):
        kwargs = dict(pk=self.pk)
        return "authoring:edit", [], kwargs

    @property
    def creator(self):
        return self.author

    @property
    def authors(self):
        return [self.author.get_full_name()]

    # TODO: move all method below to mixin class
    @property
    def member_activities(self):
        activities = []
        if self.tags.all().count():
            activities.append(TAGGED)
        if self.reviews.all().count():
            activities.append(REVIEWED)
        if self.ratings.all().count():
            activities.append(RATED)
        return activities

    @property
    def rating(self):
        ratings = self.ratings.all()
        if ratings.count():
            return ratings.aggregate(rating=models.Avg("value"))["rating"]
        return 0.0

    def keyword_slugs(self, exclude_microsite_markers=True):
        if exclude_microsite_markers:
            microsite_markers = set()
            for microsite in Microsite.objects.all():
                microsite_markers.update(microsite.keywords.values_list("slug", flat=True))
            keywords = set(self.keywords.exclude(slug__in=microsite_markers).values_list("slug", flat=True))
            keywords.update(self.tags.exclude(slug__in=microsite_markers).values_list("slug", flat=True))
        else:
            keywords = set(self.keywords.values_list("slug", flat=True))
            keywords.update(self.tags.values_list("slug", flat=True))
        return sorted(keywords)

    def keyword_names(self, exclude_microsite_markers=True):
        if exclude_microsite_markers:
            microsite_markers = set()
            for microsite in Microsite.objects.all():
                microsite_markers.update(microsite.keywords.values_list("slug", flat=True))
            keywords = set(self.keywords.exclude(slug__in=microsite_markers).values_list("name", flat=True))
            keywords.update(self.tags.exclude(slug__in=microsite_markers).values_list("name", flat=True))
        else:
            keywords = set(self.keywords.values_list("name", flat=True))
            keywords.update(self.tags.values_list("name", flat=True))
        return sorted(keywords)

    def microsites(self):
        return Microsite.objects.filter(keywords__slug__in=self.keyword_slugs(exclude_microsite_markers=False))

    def topics(self):
        microsites = self.microsites()
        if not microsites.count():
            return []
        topics = set()
        for microsite in self.microsites():
            topics_qs = microsite.topics.exclude(other=True).filter(keywords__slug__in=self.keyword_slugs())
            if topics_qs.count():
                topics.update(topics_qs)
            else:
                try:
                    topics.add(microsite.topics.get(other=True))
                except Topic.DoesNotExist:
                    pass
        return sorted(topics)

    def indexed_topics(self):
        topics = self.topics()
        if len(topics) == 1 and topics[0].other == True:
            return topics
        indexed_topics = set(topics)
        for topic in topics:
            indexed_topics.update(topic.get_ancestors())
        return list(indexed_topics)

    @property
    def visits(self):
        return Visit.objects.get_visits_count(self, None)

    @property
    def is_displayed(self):
        return self.workflow_state == PUBLISHED_STATE

    @property
    def is_evaluated(self):
        content_type = ContentType.objects.get_for_model(self)
        return Evaluation.objects.filter(
            content_type=content_type,
            object_id=self.id,
            confirmed=True).exists()

    @property
    def indexed_alignment_standards(self):
        return self.alignment_tags.values_list("tag__standard__id", flat=True).order_by().distinct()

    @property
    def indexed_alignment_grades(self):
        grades = []
        for grade, end_grade in self.alignment_tags.values_list("tag__grade__code", "tag__end_grade__code").order_by().distinct():
            grades.append("%s-%s" % (grade, end_grade) if grade else grade)
        return grades

    @property
    def indexed_alignment_categories(self):
        return self.alignment_tags.values_list("tag__category__id", flat=True).order_by().distinct()

    @property
    def all_grades(self):
        grades = set(self.grades.all())
        for grade, grade_order, end_grade, end_grade_order in self.alignment_tags.values_list(
            "tag__grade__id", "tag__grade__order",
            "tag__end_grade__id", "tag__end__order",
        ).order_by().distinct():
            if end_grade:
                grades.update(set(Grade.objects.filter(order__gte=grade_order, order__lte=end_grade_order)))
            else:
                grades.add(Grade.objects.get(pk=grade))
        return grades

    @property
    def all_grades(self):
        grades = set(self.grades.all())
        for grade, grade_order, end_grade, end_grade_order in self.alignment_tags.values_list(
            "tag__grade__id", "tag__grade__order",
            "tag__end_grade__id", "tag__end_grade__order",
        ).order_by().distinct():
            if end_grade:
                grades.update(set(Grade.objects.filter(order__gte=grade_order, order__lte=end_grade_order)))
            else:
                grades.add(Grade.objects.get(pk=grade))
        if self.grade_sublevels.exists():
            grades.update(set(Grade.objects.filter(grade_sublevel__in=self.grade_sublevels.all())))
        if self.grade_levels.exists():
            grades.update(set(Grade.objects.filter(grade_sublevel__grade__level__in=self.grade_levels.all())))
        return grades
    
    @property
    def all_grade_sublevels(self):
        sublevels = set(self.grade_sublevels.all())
        if self.grade_levels.exists():
            sublevels.update(set(GradeSubLevel.objects.filter(grade__level__in=self.grade_levels.all())))
        return sublevels 

    @property
    def all_grade_levels(self):
        return set(self.grade_levels.all())
    
    @property
    def indexed_grades(self):
        return sorted(self.all_grades, key=lambda x: x.id)

    @property
    def indexed_grade_sublevels(self):
        grade_sublevels = self.all_grade_sublevels
        for grade in self.indexed_grades:
            if grade.grade_sublevel:
                grade_sublevels.add(grade.grade_sublevel)
        return sorted(grade_sublevels, key=lambda x: x.id)
    
    @property
    def indexed_grade_levels(self):
        grade_levels = self.all_grade_levels
        for sublevel in self.indexed_grade_sublevels:
            grade_levels.add(sublevel.grade_level)
        return sorted(grade_levels, key=lambda x: x.id)


def upload_to(prefix):
    def func(instance, filename):
        return os.path.join("authoring", str(instance.material.id), prefix, filename)
    return func


class Image(models.Model):

    material = models.ForeignKey(AuthoredMaterial)

    image = models.ImageField(upload_to=upload_to("images"), max_length=500)


class Document(models.Model):

    material = models.ForeignKey(AuthoredMaterial)

    file = models.FileField(upload_to=upload_to("documents"), max_length=500)


class Embed(models.Model):

    url = models.URLField(unique=True, db_index=True, max_length=200)
    type = models.CharField(db_index=True, max_length=20)
    title = models.CharField(max_length=500, null=True, blank=True)
    embed_url = models.URLField(db_index=True, max_length=200, null=True, blank=True) # This is used for photo embeds
    thumbnail = models.URLField(db_index=True, max_length=200, null=True, blank=True)
    html = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.url

    @classmethod
    def get_for_url(cls, url):
        if cls.objects.filter(url=url).exists():
            return cls.objects.get(url=url)

        client = embedly.Embedly(settings.EMBEDLY_KEY)
        if client.is_supported(url):
            result = client.oembed(url, maxwidth="500")
            url = result.url or result.original_url

            if cls.objects.filter(url=url).exists():
                return cls.objects.get(url=url)

            return cls.objects.create(
                url=url,
                type=result.type,
                title=result.title,
                embed_url=url,
                thumbnail=result.thumbnail_url,
                html=result.html,
            )

        return None


class UploadedVideo(models.Model):

    SUPPORTED_CONTENT_TYPES = (
        "video/mpeg",
        "video/quicktime",
        "video/x-msvideo",
        "video/mp4",
        "video/x-flv",
    )

    material = models.ForeignKey(AuthoredMaterial)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    youtube_id = models.CharField(max_length=100)
    url = models.URLField(db_index=True, max_length=200, null=True, blank=True)
    html = models.TextField(null=True, blank=True)

    @classmethod
    def get_yt_service(cls):
        yt_service = gdata.youtube.service.YouTubeService()
        yt_service.email = settings.YOUTUBE_EMAIL
        yt_service.password = settings.YOUTUBE_PASSWORD
        yt_service.source = settings.YOUTUBE_SOURCE
        yt_service.developer_key = settings.YOUTUBE_DEV_KEY
        yt_service.client_id = settings.YOUTUBE_CLIENT_ID
        yt_service.ProgrammaticLogin()
        return yt_service

    @classmethod
    def upload(cls, uploaded_file, material):

        yt_service = cls.get_yt_service()

        media_group = gdata.media.Group(
            title=gdata.media.Title(text=uploaded_file.name),
            description=gdata.media.Description(
                description_type='plain',
                text=u""),
            category=[gdata.media.Category(
                 text='Education',
                 scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
                 label='Education')],
        )

        video_entry = gdata.youtube.YouTubeVideoEntry(media=media_group)
        new_entry = yt_service.InsertVideoEntry(
            video_entry,
            uploaded_file.temporary_file_path(),
            content_type=uploaded_file.content_type
        )
        youtube_id = new_entry.id.text.split("/")[-1]
        url = "http://www.youtube.com/watch?v=%s" % youtube_id
        uploaded_video = UploadedVideo.objects.create(
            material=material,
            url=url,
            youtube_id=youtube_id,
        )
        return uploaded_video.id, url, new_entry.media.thumbnail[1].url
