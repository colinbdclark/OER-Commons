

def run():
    from django.db import models
    from materials.models import CommunityItem
    from materials.models.course import Course
    from materials.models.library import Library
    from StringIO import StringIO
    import csv

    out = StringIO()

    writer = csv.writer(out)

    for model in (Course, Library, CommunityItem):
        for url, count in model.objects.values_list("url").annotate(count=models.Count("url")).filter(count__gte=2).order_by("-count"):
            for instance in model.objects.filter(url=url):
                writer.writerow((instance.slug, instance.title.encode("utf-8"), url, "http://www.oercommons.org" + instance.get_absolute_url()))

    out.seek(0)
    print out.read()
