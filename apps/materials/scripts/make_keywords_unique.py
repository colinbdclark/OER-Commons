from django.db.models.aggregates import Count
from materials.models.common import Keyword
from materials.models.community import CommunityItem
from materials.models.course import Course
from materials.models.library import Library


def run():

    duplicate_keyword_names = dict(Keyword.objects.values_list("name").annotate(id_count=Count("id")).order_by().filter(id_count__gt=1)).keys()

    for name in duplicate_keyword_names:
        keywords = Keyword.objects.filter(name=name).order_by("id")
        kw = keywords[0]
        for keyword in keywords[1:]:
            for model in (Course, Library, CommunityItem):
                items = model.objects.filter(keywords=keyword)
                for item in items:
                    item.keywords.remove(keyword)
                    if kw not in item.keywords.all():
                        item.keywords.add(kw)
            keyword.delete()
