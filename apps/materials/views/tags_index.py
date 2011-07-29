from common.models import Keyword
from django.core.urlresolvers import reverse
from django.http import HttpResponsePermanentRedirect, Http404
from django.views.generic.simple import direct_to_template
from tags.models import Tag
import string
from django.core.paginator import Paginator


COLUMNS_NUMBER = 4


def tags_index(request, letter=None):

    letters = string.ascii_lowercase

    if letter is None:
        return HttpResponsePermanentRedirect(reverse("materials:tags",
                                                     kwargs=dict(letter=letters[0])))

    if letter not in letters:
        raise Http404()

    page_title = u"Tags"
    breadcrumbs = [{"url": reverse("materials:tags", kwargs=dict(letter=letter)),
                    "title": page_title}]


    tags = dict(Tag.objects.filter(slug__startswith=letter).values_list("slug", "name"))
    tags.update(dict(Keyword.objects.filter(slug__startswith=letter).values_list("slug", "name")))

    tags = sorted(tags.items())

    batch_size = len(tags) / COLUMNS_NUMBER

    paginator = Paginator(tags, batch_size)
    columns = []
    for i in xrange(paginator.num_pages):
        columns.append(paginator.page(i + 1).object_list)

    return direct_to_template(request, "materials/tags.html", locals())
