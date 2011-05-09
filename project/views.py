from annoying.decorators import ajax_request
from cache_utils.decorators import cached
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template
from haystack.query import SearchQuerySet
from materials.models.common import Keyword, GeneralSubject, GradeLevel
from materials.models.microsite import Microsite
from materials.utils import get_name_from_slug, get_facets_for_field
from oauth_provider.models import Token
from tags.models import Tag
from tags.tags_utils import get_tag_cloud
import dateutil.parser
import re
import twitter


MAX_TAGS = 30
SCREEN_NAME = "OERCommons"
MAX_TWEETS = 5


def urlize(text):
    # Code snippet taken from http://stackoverflow.com/questions/1112012/replace-url-with-a-link-using-regex-in-python
    pat1 = re.compile(r"(^|[\n ])(([\w]+?://[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)
    pat2 = re.compile(r"#(^|[\n ])(((www|ftp)\.[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)

    text = pat1.sub(r'\1<a href="\2">\2</a>', text)
    return pat2.sub(r'\1<a href="http:/\2">http:/\2</a>', text)


def linkify_tweet(tweet):
    tweet = re.sub(r'(\A|\s)@(\w+)', r'\1@<a href="http://www.twitter.com/\2">\2</a>', tweet)
    return re.sub(r'(\A|\s)#(\w+)', r'\1#<a href="http://search.twitter.com/search?q=%23\2">\2</a>', tweet)


@cached(60 * 30)
def get_tweets():
    api = twitter.Api()
    tweets = []
    try:
        for tweet in api.GetUserTimeline(SCREEN_NAME):
            tweets.append({"text": linkify_tweet(urlize(tweet.text)),
                           "date": dateutil.parser.parse(tweet.created_at)})
            if len(tweets) >= MAX_TWEETS:
                break
    except:
        pass
    return tweets


def frontpage(request):

    keywords = get_facets_for_field("keywords")
    if len(keywords) > MAX_TAGS:
        keywords = keywords[:MAX_TAGS]
    tagcloud = get_tag_cloud(dict(keywords), max_font=4, min_font=0,
                             average_font=1)

    for keyword in tagcloud:
        name = get_name_from_slug(Keyword, keyword["slug"]) or \
               get_name_from_slug(Tag, keyword["slug"]) or \
               keyword["slug"]
        keyword["name"] = name

    general_subjects_facets = dict(get_facets_for_field("general_subjects"))
    general_subjects = list(GeneralSubject.objects.values("id", "slug", "name"))
    for s in general_subjects:
        s["count"] = general_subjects_facets.get(unicode(s["id"]), 0)


    grade_levels_facets = dict(get_facets_for_field("grade_levels"))
    grade_levels = list(GradeLevel.objects.values("id", "slug", "name"))
    for s in grade_levels:
        s["count"] = grade_levels_facets.get(unicode(s["id"]), 0)


    microsites = Microsite.objects.all()
    microsites_ids = tuple(microsites.values_list("id", flat=True))

    featured_k12 = SearchQuerySet().filter(featured=True, grade_levels__in=(1, 2)).exclude(microsites__in=microsites_ids).order_by("-featured_on").load_all()[:3]
    featured_k12 = [r.object for r in featured_k12]

    featured_highered = SearchQuerySet().filter(featured=True, grade_levels=3).exclude(microsites__in=microsites_ids).order_by("-featured_on").load_all()[:3]
    featured_highered = [r.object for r in featured_highered]

    return direct_to_template(request, "frontpage.html",
                              dict(tagcloud=tagcloud,
                                   general_subjects=general_subjects,
                                   grade_levels=grade_levels,
                                   microsites=microsites,
                                   tweets=get_tweets(),
                                   featured_k12=featured_k12,
                                   featured_highered=featured_highered,
                               ))


def contribute(request):
    page_title = u"Contribute Your Content to OER Commons"
    breadcrumbs = [{"url": reverse("contribute"), "title": page_title}]
    return direct_to_template(request, "contribute.html", locals())


@login_required
def oauth_authorize(request, token, callback, params):

    return direct_to_template(request, "oauth/authorize.html", locals())


@login_required
def oauth_callback(request, **kwargs):

    token = kwargs.pop("oauth_token", None)
    if not token:
        return redirect(reverse("frontpage"))

    token = Token.objects.get(key=token)
    return direct_to_template(request, "oauth/callback.html", locals())



@ajax_request
def honeypot(request):
    value = settings.HONEYPOT_VALUE
    if callable(value):
        value = value()
    return dict(value=value)