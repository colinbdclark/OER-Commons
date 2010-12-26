from django.template import Library
from oai import DATETIME_FORMAT


register = Library()


@register.filter
def oai_date(datetime):
    return datetime.strftime(DATETIME_FORMAT)
