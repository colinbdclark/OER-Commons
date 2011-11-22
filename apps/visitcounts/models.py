from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
import datetime
import re


ROBOT_RE = re.compile("bot|crawler|spider", re.I)


class VisitManager(models.Manager):

    def count(self, request, instance):
        ''' Count a visit for a given instance. Use session key to distinguish
        visits from different users. Count only if current user has visited
        the instance at least an hour ago or haven't visited at all. '''

        user_agent = request.META.get("HTTP_USER_AGENT")
        if user_agent and ROBOT_RE.search(user_agent):
            return

        session_key = request.session.session_key
        content_type = ContentType.objects.get_for_model(instance)
        object_id = instance.id
        if not Visit.objects.filter(session_key=session_key,
                              content_type=content_type,
                              object_id=object_id,
                              timestamp__gte=datetime.datetime.now() - datetime.timedelta(hours=1)).exists():
            Visit.objects.create(session_key=session_key,
                                 content_type=content_type,
                                 object_id=object_id)

    def get_visits_count(self, instance, period=datetime.timedelta(days=30)):
        kwargs = dict(content_type=ContentType.objects.get_for_model(instance),
                      object_id=instance.id)
        if period:
            kwargs["timestamp__gte"] = datetime.datetime.now() - period
        return Visit.objects.filter(**kwargs).count()


class Visit(models.Model):

    session_key = models.CharField(max_length=32, db_index=True)

    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_(u"Content type"), db_index=True)
    object_id = models.PositiveIntegerField(verbose_name=_(u"Object ID"), db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    timestamp = models.DateTimeField(auto_now_add=True,
                                     default=datetime.datetime.now,
                                     db_index=True)
    objects = VisitManager()
