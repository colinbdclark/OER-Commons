from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from information.models import HelpTopic, AboutTopic


def information(request):

    page_title = u"OER Commons Help and About"
    breadcrumbs = [{"url": reverse("information"), "title": page_title}]

    help_topics = HelpTopic.objects.all()
    about_topics = AboutTopic.objects.all()

    return direct_to_template(request, "information/information.html", locals())


def help(request):
    page_title = u"OER Commons Help"
    breadcrumbs = [{"url": reverse("help"), "title": page_title}]

    topics = HelpTopic.objects.all()

    return direct_to_template(request, "information/topics.html", locals())


def about(request):
    page_title = u"About"
    breadcrumbs = [{"url": reverse("about"), "title": page_title}]

    topics = AboutTopic.objects.all()

    return direct_to_template(request, "information/topics.html", locals())
