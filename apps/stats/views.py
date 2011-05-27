from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.db import models
from django.http import Http404
from django.views.generic.simple import direct_to_template
from materials.models.community import CommunityItem
from materials.models.course import Course
from materials.models.library import Library
from rating.models import Rating
from reviews.models import Review
from saveditems.models import SavedItem
from tags.models import Tag
from users.models import Profile, MEMBER_ROLES
from utils.decorators import login_required
import datetime
import urllib


PERIODS = (
    (u"All time", None),
    (u"1 day", datetime.timedelta(days=1)),
    (u"1 week", datetime.timedelta(days=7)),
    (u"1 month", datetime.timedelta(days=30)),
    (u"3 months", datetime.timedelta(days=90)),
    (u"1 year", datetime.timedelta(days=365)),
)


def get_users_submitted_count(from_date=None, until_date=None):
    filter = {}
    if from_date:
        filter["created_on__gte"] = from_date
    if until_date:
        filter["created_on__lt"] = until_date
    return len(set(list(Course.objects.filter(**filter).values_list("creator__id").distinct()) + \
                   list(Library.objects.filter(**filter).values_list("creator__id").distinct()) + \
                   list(CommunityItem.objects.filter(**filter).values_list("creator__id").distinct())))


def get_users_commented_count(from_date=None, until_date=None):
    filter = {}
    if from_date:
        filter["timestamp__gte"] = from_date
    if until_date:
        filter["timestamp__lt"] = until_date
    return Review.objects.filter(**filter).values_list("user__id").distinct().count()


def get_users_rated_count(from_date=None, until_date=None):
    filter = {}
    if from_date:
        filter["timestamp__gte"] = from_date
    if until_date:
        filter["timestamp__lt"] = until_date
    return Rating.objects.filter(**filter).values_list("user__id").distinct().count()


def get_users_saveditems_count(from_date=None, until_date=None):
    filter = {}
    if from_date:
        filter["timestamp__gte"] = from_date
    if until_date:
        filter["timestamp__lt"] = until_date
    return SavedItem.objects.filter(**filter).values("user__id").annotate(count=models.Count("user__id")).filter(count__gt=5).count()


def get_users_tagged_count(from_date=None, until_date=None):
    filter = {}
    if from_date:
        filter["timestamp__gte"] = from_date
    if until_date:
        filter["timestamp__lt"] = until_date
    return Tag.objects.filter(**filter).values_list("user__id").distinct().count()


def get_registrations_count(from_date=None, until_date=None):
    filter = {}
    if from_date:
        filter["date_joined__gte"] = from_date
    if until_date:
        filter["date_joined__lt"] = until_date
    filter["is_active"] = True
    return User.objects.filter(**filter).count() 


STATS = (
    (u"How many users have submitted resources?", get_users_submitted_count),
    (u"How many users have commented on at least one item?", get_users_commented_count),
    (u"How many users have rated at least one item?", get_users_rated_count),
    (u"How many users have tagged at least one item?", get_users_tagged_count),
    (u"How many users have more than five items bookmarked?", get_users_saveditems_count),
    (u"New registered members", get_registrations_count),
)


@login_required
def stats(request, period=None):

    if not request.user.is_staff:
        raise Http404()

    if period is None:
        period = PERIODS[0]
    else:
        try:
            period = PERIODS[int(period) - 1]
        except:
            raise Http404()
        
    timedelta = period[1]
    kwargs = dict()
    from_date = None
    if timedelta:
        from_date = datetime.datetime.now() - timedelta
        kwargs["from_date"] = from_date
        
    stats = []
    for title, getter in STATS:
        stats.append(dict(title=title, value=getter(**kwargs)))

    profile_qs = Profile.objects.filter(user__is_active=True)
    if from_date:
        profile_qs = profile_qs.filter(user__date_joined__gte=from_date)
    role_counts = dict(profile_qs.values_list("role").annotate(count=models.Count("role")))
    roles = []
    for role, role_name in MEMBER_ROLES:
        roles.append(dict(name=role_name, count=role_counts.get(role, 0)))
    roles.append(dict(name=u"Not specified", count=role_counts.get("", 0)))
    
    params = {}
    chxl = []
    for role in roles:
        chxl.append(unicode(role["name"]))
            
    params["chbh"] = "a"
    params["chs"] = "300x198"
    params["cht"] = "bhs"
    params["chco"] = "4D89F9"
    params["chd"] = "t:%s" % ",".join([str(v["count"]) for v in roles])
    params["chds"] = "0,%i" % max([v["count"] for v in roles])
    params["chbh"] = "a,5"
    roles_graph_url = "http://chart.apis.google.com/chart?%s" % urllib.urlencode(params)
    
    
    return direct_to_template(request, "stats/stats.html",
                              dict(
                                selected_period=PERIODS.index(period) + 1,
                                periods=[p[0] for p in PERIODS],
                                stats=stats,
                                roles=roles,
                                roles_graph_url=roles_graph_url,
                                page_title=u"Statistics",
                              ))


@login_required
def graph(request, graph=None):

    if not request.user.is_staff:
        raise Http404()

    try:
        graph = STATS[int(graph) - 1]
    except:
        raise Http404()
        
    title, getter = graph
    
    date_ranges = []
    now = datetime.date.today()
    if now.day != 1:
        date_ranges.append((now.replace(day=1), now))
        
    now = now.replace(day=1)
    delta = relativedelta(months=1)
    for i in xrange(12 - len(date_ranges)):
        _prev = now - delta
        date_ranges.append((_prev, now))
        now = _prev
    
    data = []
    for from_date, until_date in date_ranges:
        data.append((from_date, getter(from_date=from_date, until_date=until_date)))

    data.reverse()

    params = {}
    chxl = []
    for i, d in enumerate(data):
        if i == 0 or i == len(data) - 1:
            chxl.append(d[0].strftime("%b, %Y"))
        else:
            chxl.append(d[0].strftime("%b"))
            
    params["chxl"] = "1:|" + "|".join(chxl)
    params["chxr"] = "0,0,%i" % max([v[1] for v in data])
    params["chxt"] = "y,x"
    params["chbh"] = "a"
    params["chs"] = "550x300"
    params["cht"] = "bvg"
    params["chco"] = "A2C180"
    params["chd"] = "t:%s" % ",".join([str(v[1]) for v in data])
    params["chtt"]= title
    params["chf"] = "bg,s,67676700"
                
    graph_url = "http://chart.apis.google.com/chart?%s" % urllib.urlencode(params)
        
    return direct_to_template(request, "stats/graph.html",
                              dict(
                                graph_url=graph_url,
                                page_title=title,
                              ))
    