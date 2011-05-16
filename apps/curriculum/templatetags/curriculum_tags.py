from django.template import Library


register = Library()


@register.inclusion_tag("curriculum/include/align-form.html", takes_context=True)
def align_form(context):
    return dict()