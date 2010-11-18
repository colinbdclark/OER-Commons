from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('materials.views',
    url(r'^browse$', 'index.index'),
)
