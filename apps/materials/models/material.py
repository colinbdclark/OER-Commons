from autoslug.fields import AutoSlugField
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.core.signals import request_finished
from django.db import models
from django.db.models import permalink
from django.db.models.aggregates import Avg
from django.utils.translation import ugettext_lazy as _
from materials import globals
from materials.models import License
from materials.models.common import AutoCreateForeignKey
from materials.models.microsite import Microsite, Topic
from materials.tasks import check_url_status
from rating.models import Rating
from reviews.models import Review
from saveditems.models import SavedItem
from tags.models import Tag
from visitcounts.models import Visit
import datetime


PUBLISHED_STATE = u"published"
PRIVATE_STATE = "private"
PENDING_STATE = u"pending"
REJECTED_STATE = u"rejected"


WORKFLOW_STATES = (
   (PUBLISHED_STATE, _(u"Published")),
   (PRIVATE_STATE, _(u"Private")),
   (PENDING_STATE, _(u"Pending")),
   (REJECTED_STATE, _(u"Rejected")),
)


WORKFLOW_TRANSITIONS = (
    {"id": "request_review", "from": [PRIVATE_STATE, REJECTED_STATE], "to": PENDING_STATE, "title": u"Request review", "condition": lambda user, object: object.creator == user and not user.is_staff},
    {"id": "publish", "from": [PRIVATE_STATE, PENDING_STATE, REJECTED_STATE], "to": PUBLISHED_STATE, "title": u"Publish", "condition": lambda user, object: user.is_staff},
    {"id": "reject", "from": [PENDING_STATE, PUBLISHED_STATE], "to": REJECTED_STATE, "title": u"Reject", "condition": lambda user, object: object.creator != user and user.is_staff},
    {"id": "retract", "from": [PENDING_STATE, PUBLISHED_STATE, REJECTED_STATE], "to": PRIVATE_STATE, "title": u"Retract", "condition": lambda user, object: object.creator == user},
)


RATED = u"rated"
REVIEWED = u"reviewed"
TAGGED = u"tagged"

MEMBER_ACTIVITY_TYPES = (
    (RATED, u'Only Items with Ratings'),
    (REVIEWED, u'Only Items with Reviews'),
    (TAGGED, u'Only Items with Tags'),
)


class Material(models.Model):

    namespace = None

    title = models.CharField(max_length=500, verbose_name=_(u"Title"))
    slug = AutoSlugField(max_length=500, populate_from='title', unique=True,
                         verbose_name=_(u"Slug"))

    created_on = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_(u"Created on"))
    modified_on = models.DateTimeField(auto_now=True, null=True, blank=True,
                                      verbose_name=_(u"Modified on"))

    workflow_state = models.CharField(max_length=50, default=u"private",
                                      choices=WORKFLOW_STATES,
                                      verbose_name=_(u"Workflow state"))
    published_on = models.DateTimeField(null=True, blank=True,
                                        verbose_name=_(u"Published on"))

    creator = models.ForeignKey(User, verbose_name=_("Creator"))

    license = AutoCreateForeignKey(License, verbose_name=_(u"License"),
                                   respect_all_fields=True)

    in_rss = models.BooleanField(default=False,
                                 verbose_name=_(u"Include in RSS"))
    rss_description = models.TextField(default=u"", blank=True,
                                       verbose_name=_(u"RSS Description"))
    rss_timestamp = models.DateTimeField(null=True, blank=True,
                                         verbose_name=_(u"RSS Date/Time"))

    featured = models.BooleanField(default=False, verbose_name=_(u"Featured"))
    featured_on = models.DateTimeField(null=True, blank=True)
    
    http_status = models.IntegerField(null=True, blank=True, verbose_name=_(u"HTTP Status"))

    tags = generic.GenericRelation(Tag)
    reviews = generic.GenericRelation(Review)
    saved_items = generic.GenericRelation(SavedItem)
    ratings = generic.GenericRelation(Rating)
    
    @property
    def verbose_name(self):
        return self._meta.verbose_name

    @property
    def verbose_name_plural(self):
        return self._meta.verbose_name_plural

    def save(self, *args, **kwargs):
        if self.workflow_state == PUBLISHED_STATE and not self.published_on:
            self.published_on = datetime.datetime.now()
        if self.featured and not self.featured_on:
            self.featured_on = datetime.datetime.now()
        if not self.featured:
            self.featured_on = None
        super(Material, self).save(*args, **kwargs)

    @permalink
    def get_absolute_url(self):
        return ("materials:%s:view_item" % self.namespace, [], {"slug": self.slug})

    @classmethod
    @permalink
    def get_parent_url(self):
        return ("materials:%s:index" % self.namespace, [], {})

    def breadcrumbs(self):
        breadcrumbs = []
        breadcrumbs.append({"url": self.get_parent_url(),
                            "title": self._meta.verbose_name_plural})
        breadcrumbs.append({"url": self.get_absolute_url(),
                            "title": self.title})
        return breadcrumbs

    class Meta:
        app_label = "materials"
        abstract = True

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
            return ratings.aggregate(rating=Avg("value"))["rating"]
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
        return self.workflow_state == PUBLISHED_STATE and self.http_status != 404


def mark_for_reindex(sender, **kwargs):
    to_be_reindexed = getattr(globals, "to_be_reindexed", {})
    if sender not in to_be_reindexed:
        to_be_reindexed[sender] = set()
    to_be_reindexed[sender].add(kwargs["instance"])
    if len(to_be_reindexed[sender]) > getattr(settings, 'HAYSTACK_BATCH_SIZE', 1000):
        reindex_materials()
    globals.to_be_reindexed = to_be_reindexed


def reindex_materials(**kwargs):
    to_be_reindexed = getattr(globals, "to_be_reindexed", {})
    from haystack.sites import site
    for model, objects in to_be_reindexed.items():
        index = site.get_index(model)
        index.backend.update(index, objects)
    globals.to_be_reindexed = {}
request_finished.connect(reindex_materials, dispatch_uid="materials_request_finished_reindex")


def unindex_material(sender, **kwargs):
    instance = kwargs["instance"]
    to_be_reindexed = getattr(globals, "to_be_reindexed", {})
    if sender in to_be_reindexed:
        to_be_reindexed[sender].discard(instance)
    from haystack.sites import site
    site.remove_object(instance)


def check_material_url(sender, **kwargs):
    instance = kwargs["instance"]
    check_url_status.delay(instance)
