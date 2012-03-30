from annoying.decorators import ajax_request
from django.http import Http404
from materials.models.common import License, CC_LICENSE_URL_RE
from utils.decorators import login_required


@login_required
@ajax_request
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
        license_type = CC_LICENSE_URL_RE.search(result["url"]).groupdict()["cc_type"]
        response["license_classes"] = license_type.split("-")
    else:
        response["status"] = "error"
        response["message"] = u"Unable to get license information from CreativeCommons.org. Try again later."

    return response

