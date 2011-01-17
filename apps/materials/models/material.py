from autoslug.fields import AutoSlugField
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.db import models
from django.db.models import permalink
from django.db.models.aggregates import Avg
from django.utils.translation import ugettext_lazy as _
from materials.models import License
from materials.models.common import AutoCreateForeignKey
from notes.models import Note
from rating.models import Rating
from reviews.models import Review
from saveditems.models import SavedItem
from tags.models import Tag
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

    tags = generic.GenericRelation(Tag)
    reviews = generic.GenericRelation(Review)
    notes = generic.GenericRelation(Note)
    saved_items = generic.GenericRelation(SavedItem)
    ratings = generic.GenericRelation(Rating)

    def save(self, *args, **kwargs):
        if self.workflow_state == PUBLISHED_STATE and not self.published_on:
            self.published_on = datetime.datetime.now()
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
