from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from materials.models.material import WORKFLOW_TRANSITIONS
from utils.decorators import login_required


@login_required
def transition(request, slug=None, model=None, transition_id=None):

    item = get_object_or_404(model, slug=slug)
    transition = None
    for t in WORKFLOW_TRANSITIONS:
        if t["id"] == transition_id and item.workflow_state in t["from"] and t["condition"](request.user, item):
            transition = t
            break

    if transition is None:
        raise Http404()

    item.workflow_state = t["to"]
    item.save()
    messages.success(request, u"Item status was changed to \"%s\"" % item.get_workflow_state_display())

    return redirect(item)
