from django.contrib.sitemaps import GenericSitemap as BaseGenericSitemap, \
    Sitemap
from django.core.urlresolvers import reverse
from materials.models.common import GeneralSubject, GradeLevel
from materials.models.community import CommunityItem, CommunityType, \
    CommunityTopic
from materials.models.course import Course, CourseMaterialType
from materials.models.library import Library, LibraryMaterialType
from materials.models.material import PUBLISHED_STATE
import datetime


now = datetime.datetime.now()


class GenericSitemap(BaseGenericSitemap):
    limit = 1000


class LastmodGenedicSitemap(GenericSitemap):
    lastmod = now


class StaticPagesSitemap(Sitemap):
    changefreq = "daily"
    lastmod = now 

    def location(self, item):
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
            ("materials:courses:course_or_module_index", [], {"course_or_module": "full-course"}),
            ("materials:courses:course_or_module_index", [], {"course_or_module": "learning-module"}),
            ("materials:community", [], {}),
            ("feedback", [], {}),
        ]
        return items
        

sitemaps = {
    'static': StaticPagesSitemap(),
    'library-material-types': LastmodGenedicSitemap(dict(queryset=LibraryMaterialType.objects.all()), changefreq="daily"),
    'general-subjects': LastmodGenedicSitemap(dict(queryset=GeneralSubject.objects.all()), changefreq="daily"),
    'grade-levels': LastmodGenedicSitemap(dict(queryset=GradeLevel.objects.all()), changefreq="daily"),
    'course-material-types': LastmodGenedicSitemap(dict(queryset=CourseMaterialType.objects.all()), changefreq="daily"),
    'community-types': LastmodGenedicSitemap(dict(queryset=CommunityType.objects.all()), changefreq="daily"),
    'community-topics': LastmodGenedicSitemap(dict(queryset=CommunityTopic.objects.all()), changefreq="daily"),
    'courses': GenericSitemap(dict(queryset=Course.objects.filter(workflow_state=PUBLISHED_STATE).exclude(http_status=404), date_field="published_on")),
    'libraries': GenericSitemap(dict(queryset=Library.objects.filter(workflow_state=PUBLISHED_STATE).exclude(http_status=404), date_field="published_on")),
    'community': GenericSitemap(dict(queryset=CommunityItem.objects.filter(workflow_state=PUBLISHED_STATE).exclude(http_status=404), date_field="published_on")),
}


