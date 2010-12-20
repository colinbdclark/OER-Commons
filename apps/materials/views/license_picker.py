from django.http import Http404, HttpResponse
from materials.models.common import License
from utils.decorators import login_required
import cjson


@login_required
def issue(request):
    if request.method != "POST":
        raise Http404()

    fields = License.objects.get_cc_issue_fields()
    answers = {}
    for field in fields:
        answers[field["id"]] = request.POST.get("cc-question-%s" % field["id"], u'')

    response = {"status": "error"}
    result = License.objects.issue(answers)
    if result:
        response["status"] = "success"
        response.update(result)
    else:
        response["status"] = "error"
        response["message"] = u"Unable to get license information from CreativeCommons.org. Try again later."

    return HttpResponse(cjson.encode(response),
                        content_type="application/json")

