from django.contrib.sites.models import Site
from django.views.generic.simple import direct_to_template
from materials.models.course import Course
from materials.models.library import Library
from materials.models.material import PUBLISHED_STATE


MAX_ITEMS = 20


def facebook_feed(request):
    
    items = set()
    items.update(Course.objects.filter(workflow_state=PUBLISHED_STATE,
                                       in_rss=True).exclude(rss_timestamp=None, http_status=404).order_by("-rss_timestamp").select_related()[:MAX_ITEMS])
    items.update(Library.objects.filter(workflow_state=PUBLISHED_STATE,
                                        in_rss=True).exclude(rss_timestamp=None, http_status=404).order_by("-rss_timestamp").select_related()[:MAX_ITEMS])
    
    items = sorted(items, key=lambda x: x.rss_timestamp, reverse=True)
    if len(items) > MAX_ITEMS:
        items = items[:MAX_ITEMS]
        
    for item in items:
        item.tag_names = item.tags.values_list("name", flat=True)
        
    site_url = "http://%s" % Site.objects.get_current().domain
    
    return direct_to_template(request, "materials/facebook-feed.xml", locals(),
                              "text/xml")