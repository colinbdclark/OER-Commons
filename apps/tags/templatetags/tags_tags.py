from django.template import Library


register = Library()


@register.inclusion_tag("tags/include/add-tags-form.html", takes_context=True)
def add_tags_form(context):
    return dict()
