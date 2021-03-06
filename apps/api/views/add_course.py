from annoying.decorators import ajax_request
from api.decorators import api_method
from django.contrib.sites.models import Site
from materials.models.common import Collection
from materials.models.material import PUBLISHED_STATE, PRIVATE_STATE
from materials.views.forms.course.add import AddForm
from oauth_provider.decorators import oauth_required


@oauth_required
@api_method
@ajax_request
def add_course(request):

    form = AddForm(request.REQUEST)

    if form.is_valid():
        object = form.save(commit=False)
        object.collection = Collection.objects.get_or_create(name=u"Individual Authors")[0]
        object.creator = request.user
        if request.user.is_staff:
            object.workflow_state = PUBLISHED_STATE
        else:
            object.workflow_state = PRIVATE_STATE
        object.save()
        form.save_m2m()
        return dict(status="success",
                     url="http://%s%s" % (Site.objects.get_current(),
                                          object.get_absolute_url()))
    else:
        return dict(errors=form._errors)
