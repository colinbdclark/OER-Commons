from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from haystack_scheduled.indexes import Indexed
from utils import update_item
import re
import json


ROBOT_RE = re.compile("bot|crawler|spider", re.I)


class VisitCounterManager(models.Manager):

    def manage_count(self, instance):
        content_type = ContentType.objects.get_for_model(instance)
        object_id = instance.id

        visit_counter, created = VisitCounter.objects.get_or_create(
            content_type=content_type,
            object_id=object_id
        )
        visits = visit_counter.visits + 1
        update_item(visit_counter, visits=visits)

        if visits % 10 == 0:
            if isinstance(instance, Indexed):
                instance.reindex()

    def count_item(self, request, response, instance):
        ''' Count a visit for a given instance. Use session key to distinguish
        visits from different users.
        '''
        user_agent = request.META.get("HTTP_USER_AGENT")
        if user_agent and ROBOT_RE.search(user_agent):
            return

        # Checks uniqueness of the visitors for different items and updates cookies.
        current_cookies = request.COOKIES.get("visits", None)
        content_type = ContentType.objects.get_for_model(instance)
        content_type_id = str(content_type.id)
        new_cookies = {}

        if current_cookies:
            visits = json.loads(current_cookies)

            if content_type_id in visits.keys():
                object_ids = visits[content_type_id]

                if object_ids:
                    if instance.id not in object_ids:
                        object_ids.append(instance.id)
                        new_cookies[content_type_id] = object_ids
                        self.manage_count(instance)
                    else:
                        new_cookies[content_type_id] = object_ids

        if not new_cookies:
            new_cookies[content_type_id] = [instance.id]
            self.manage_count(instance)

        visits = json.dumps(new_cookies, separators=(",", ":"))
        response.set_cookie('visits', visits)
        return response

    def get_visits_count(self, instance):
        visit_counter, created = VisitCounter.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id
        )
        return visit_counter.visits


class VisitCounter(models.Model):

    visits = models.IntegerField(verbose_name=_(u"Counter"), default=0,
                                  editable=False)

    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_(u"Content type"),
        db_index=True
    )
    object_id = models.PositiveIntegerField(verbose_name=_(u"Object ID"),
                                            db_index=True)
    content_object = generic.GenericForeignKey()

    objects = VisitCounterManager()
