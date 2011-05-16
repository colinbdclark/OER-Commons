from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("curriculum.views",
    url(r"^curriculum/align/(\w+)/(\w+)/(\d+)/?$", "align", name="align"),
    url(r"^curriculum/list_standards/?$", "list_standards", name="list_standards"),
    url(r"^curriculum/list_grades/?$", "list_grades", name="list_grades"),
    url(r"^curriculum/list_categories/?$", "list_categories", name="list_categories"),
    url(r"^curriculum/list_tags/?$", "list_tags", name="list_tags"),
)