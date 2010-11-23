from cache_utils.decorators import cached
from django.views.generic.simple import direct_to_template
from materials.models.common import Keyword, GeneralSubject, GradeLevel
from materials.utils import get_name_from_slug, get_facets_for_field
from tags.models import Tag
from tags.utils import get_tag_cloud
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


    return direct_to_template(request, "frontpage.html",
                              dict(tagcloud=tagcloud,
                                   general_subjects=general_subjects,
                                   grade_levels=grade_levels,
                                   tweets=get_tweets(),
                               ))
