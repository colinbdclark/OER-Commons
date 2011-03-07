from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("stats.views",
    url(r"^statistics(?:/(?P<period>\d+))?/?$", "stats", name="stats"),
    url(r"^statistics/graph/(?P<graph>\d+)?/?$", "graph", name="stats_graph"),
)