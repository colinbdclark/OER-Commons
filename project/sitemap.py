from common.models import GradeLevel
from django.contrib.sitemaps import GenericSitemap as BaseGenericSitemap, \
    Sitemap
from django.core.urlresolvers import reverse
from materials.models.common import GeneralSubject
from materials.models.community import CommunityItem, CommunityType, \
    CommunityTopic
from materials.models.course import Course, CourseMaterialType
from materials.models.library import Library, LibraryMaterialType
from materials.models.material import PUBLISHED_STATE
import datetime


now = datetime.datetime.now()


class GenericSitemap(BaseGenericSitemap):
    limit = 1000


class OERSitemap(Sitemap):
    changefreq = "daily"
    lastmod = now

    def location(self, item):
        if hasattr(item, "get_absolute_url"):
            return item.get_absolute_url()
        view_name, args, kwargs = item
        return reverse(view_name, args=args, kwargs=kwargs)

    def items(self):
        items = [
            ("frontpage", [], {}),
            ("materials:browse", [], {}),
            ("materials:browse_providers", [], {}),
            ("information", [], {}),
            ("help", [], {}),
            ("about", [], {}),
            ("contribute", [], {}),
            ("users:registration", [], {}),
        ]
        items += list(LibraryMaterialType.objects.all())
        items += list(GeneralSubject.objects.all())
        items += list(GradeLevel.objects.all())

        items += [
            ("materials:courses:course_or_module_index", [], {"course_or_module": "full-course"}),
            ("materials:courses:course_or_module_index", [], {"course_or_module": "learning-module"}),
        ]

        items += list(CourseMaterialType.objects.all())

        items += [
            ("materials:community", [], {}),
        ]
        items += list(CommunityType.objects.all())
        items += list(CommunityTopic.objects.all())

        items += [
            ("feedback", [], {}),
        ]

        return items


sitemaps = {
    'main': OERSitemap(),
    'courses': GenericSitemap(dict(queryset=Course.objects.filter(workflow_state=PUBLISHED_STATE).exclude(http_status=404), date_field="published_on")),
    'libraries': GenericSitemap(dict(queryset=Library.objects.filter(workflow_state=PUBLISHED_STATE).exclude(http_status=404), date_field="published_on")),
    'community': GenericSitemap(dict(queryset=CommunityItem.objects.filter(workflow_state=PUBLISHED_STATE).exclude(http_status=404), date_field="published_on")),
}


