from django.template import Library
from savedsearches.views import SaveSearchForm


register = Library()


@register.inclusion_tag("savedsearches/include/form.html", takes_context=True)
def save_search_form(context, url, title=u""):
    form = SaveSearchForm(dict(url=url, title=title))
    return dict(form=form, request=context["request"])
