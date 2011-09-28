from django.conf.urls.defaults import patterns, url
from rubrics.manage.views import Login, Index, \
    UserEvaluations, ResourceEvaluations, DeleteEvaluation, EditEvaluation


urlpatterns = patterns("",
    url(r"^login$", Login.as_view(), name="login"),
    url(r"^$", Index.as_view(), name="index"),
    url(r"^(?P<content_type_id>\d+)/(?P<object_id>\d+)$", ResourceEvaluations.as_view(), name="resource"),
    url(r"^user/(?P<user_id>\d+)$", UserEvaluations.as_view(), name="user"),
    url(r"^delete$", DeleteEvaluation.as_view(), name="delete"),
    url(r"^edit$", EditEvaluation.as_view(), name="edit"),
)
