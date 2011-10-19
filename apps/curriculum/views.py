from __future__ import absolute_import

from annoying.decorators import ajax_request
from curriculum.models import TaggedMaterial, AlignmentTag, Standard, Grade, \
    LearningObjectiveCategory
from curriculum.utils import get_item_tags as get_item_tags_helper
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Avg
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.views.generic.simple import direct_to_template
from haystack_scheduled.indexes import Indexed
from rubrics.models import StandardAlignmentScore
from utils.decorators import login_required


class TagResourceForm(forms.Form):

    tag = forms.ModelChoiceField(queryset=AlignmentTag.objects.all())

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop("instance", None)
        self.user = kwargs.pop("user", None)
        super(TagResourceForm, self).__init__(*args, **kwargs)

    def save(self):
        tag = self.cleaned_data.get("tag")
        if not self.instance or not self.user or not tag:
            return
        content_type = ContentType.objects.get_for_model(self.instance)
        object_id = self.instance.id
        tagged, created = TaggedMaterial.objects.get_or_create(user=self.user,
                                                     tag=tag,
                                                     content_type=content_type,
                                                     object_id=object_id)
        return tagged


@login_required
@ajax_request
def align(request, app_label, model, object_id):

    if request.method != "POST":
        raise Http404()

    content_type = get_object_or_404(ContentType, app_label=app_label,
                                     model=model)
    model = content_type.model_class()
    object_id = int(object_id)

    item = get_object_or_404(model, id=object_id)
    user = request.user

    form = TagResourceForm(request.POST, instance=item, user=user)
    if form.is_valid():
        tagged = form.save()
        tag = form.cleaned_data["tag"]

        if isinstance(item, Indexed):
            item.reindex()

        return dict(status="success",
                    tag=dict(id=tagged.id, code=tag.full_code,
                             url=reverse("materials:alignment_index",
                                        kwargs=dict(alignment=tag.full_code))))
    else:
        return dict(status="error")


@login_required
@ajax_request
def get_item_tags(request, app_label, model, object_id):
    content_type = get_object_or_404(ContentType, app_label=app_label,
                                     model=model)
    object_id = int(object_id)
    item = get_object_or_404(content_type.model_class(), id=object_id)
    return get_item_tags_helper(item, request.user)


@login_required
@ajax_request
def delete_tag(request):
    if request.method != "POST":
        raise Http404()

    try:
        tagged = TaggedMaterial.objects.get(id=int(request.POST["id"]))
    except:
        return dict(status="error")

    tagged.delete()
    return dict(status="success")


@ajax_request
def list_standards(request, existing=False):
    if existing:
        ids = TaggedMaterial.objects.all().values_list("tag__standard", flat=True).order_by().distinct()
    else:
        ids = AlignmentTag.objects.values_list("standard", flat=True).order_by().distinct()
    return dict(options=list(Standard.objects.filter(id__in=ids).values("id", "name")))


@ajax_request
def list_grades(request, existing=False):
    standard = request.POST.get("standard")
    try:
        standard = Standard.objects.get(id=int(standard))
    except:
        return HttpResponse(u"", status=400)

    if existing:
        ids = TaggedMaterial.objects.filter(tag__standard=standard).values_list("tag__grade", flat=True).order_by().distinct()
    else:
        ids = AlignmentTag.objects.filter(standard=standard).values_list("grade", flat=True).order_by().distinct()
    return dict(options=list(Grade.objects.filter(id__in=ids).values("id", "name")))


@ajax_request
def list_categories(request, existing=False):
    standard = request.POST.get("standard")
    try:
        standard = Standard.objects.get(id=int(standard))
    except:
        return HttpResponse(u"", status=400)

    grade = request.POST.get("grade")
    try:
        grade = Grade.objects.get(id=int(grade))
    except:
        return HttpResponse(u"", status=400)

    if existing:
        ids = TaggedMaterial.objects.filter(tag__standard=standard,
                                            tag__grade=grade).values_list("tag__category", flat=True).order_by().distinct()
    else:
        ids = AlignmentTag.objects.filter(standard=standard,
                                          grade=grade).values_list("category",
                                                                   flat=True).order_by().distinct()
    return dict(options=list(LearningObjectiveCategory.objects.filter(id__in=ids).values("id", "name")))


@ajax_request
def list_tags(request, existing=False):
    standard = request.POST.get("standard")
    try:
        standard = Standard.objects.get(id=int(standard))
    except:
        return HttpResponse(u"", status=400)

    grade = request.POST.get("grade")
    try:
        grade = Grade.objects.get(id=int(grade))
    except:
        return HttpResponse(u"", status=400)

    category = request.POST.get("category")
    try:
        category = LearningObjectiveCategory.objects.get(id=int(category))
    except:
        return HttpResponse(u"", status=400)

    if existing:
        ids = TaggedMaterial.objects.filter(tag__standard=standard,
                                            tag__grade=grade,
                                            tag__category=category).values_list("tag", flat=True).order_by().distinct()
        tags = AlignmentTag.objects.filter(id__in=ids)
    else:
        tags = AlignmentTag.objects.filter(standard=standard, grade=grade,
                                           category=category)

    optgroups = []
    items = []
    title = None

    # Group tag by subcategory and create the following structure:
    # tag1.subcategory
    # - tag1
    # - tag2 (has the same subcat as tag1)
    # - tag3 (has the same subcat as tag2)
    # tag4.subcategory
    # - tag4
    # - tag5 (has the same subcat as tag4)
    # ....

    for tag in tags:
        if tag.subcategory != title:
            # Start filling the next optgroup
            if title and items:
                optgroups.append(dict(title=title, items=items))
            title = tag.subcategory
            items = []
        items.append(dict(id=tag.id,
                          name=unicode(tag),
                          code=tag.full_code))

    if title and items:
        # Add the last optgroup to final results
        optgroups.append(dict(title=title, items=items))

    return dict(optgroups=optgroups)


class TagDescription(TemplateView):

    template_name = "curriculum/tag-description-tooltip.html"

    def get_context_data(self, **kwargs):
        code = kwargs["code"]
        content_type_id = kwargs.get("content_type_id")
        object_id = kwargs.get("object_id")
        try:
            tag = AlignmentTag.objects.get_from_full_code(code)
        except AlignmentTag.DoesNotExist:
            raise Http404()

        data = dict(tag=tag)

        if content_type_id and object_id:
            scores = StandardAlignmentScore.objects.filter(
                alignment_tag=tag,
                evaluation__content_type__id=int(content_type_id),
                evaluation__object_id=int(object_id),
            )
            data["score_value"] = None
            data["evaluations_number"] = scores.count()
            if data["evaluations_number"]:
                value = scores.aggregate(value=Avg("score__value"))["value"]
                if value is None:
                    data["score_verbose"] = u"Not Applicable"
                    data["score_class"] = "5"
                else:
                    data["score_value"] = value
                    if 2.5 < value <= 3:
                        data["score_verbose"] = u"Superior"
                        data["score_class"] = "1"
                    elif 1.5 < value <= 2.5:
                        data["score_verbose"] = u"Strong"
                        data["score_class"] = "2"
                    elif 0.5 < value <= 1.5:
                        data["score_verbose"] = u"Limited"
                        data["score_class"] = "3"
                    else:
                        data["score_verbose"] = u"Very Weak"
                        data["score_class"] = "4"
            else:
                data["score_verbose"] = u"Not Rated"
                data["score_class"] = "5"

        return data
