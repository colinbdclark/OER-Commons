from __future__ import absolute_import

from annoying.decorators import ajax_request
from common.models import Grade
from curriculum.models import TaggedMaterial, AlignmentTag, Standard,\
    LearningObjectiveCategory
from curriculum.utils import get_item_tags as get_item_tags_helper
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Avg
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from rubrics.models import StandardAlignmentScore, get_verbose_score_name, \
    Evaluation
from utils.decorators import login_required
from core.search import reindex
from utils.templatetags.utils import truncatechars
import re


class TagResourceForm(forms.Form):

    tag = forms.ModelChoiceField(queryset=AlignmentTag.objects.all())

    def __init__(self, *args, **kwargs):
        #noinspection PyArgumentEqualDefault
        self.instance = kwargs.pop("instance", None)
        #noinspection PyArgumentEqualDefault
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

        reindex(item)

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
    return dict(tags=get_item_tags_helper(item, request.user))


@login_required
@ajax_request
def delete_tag(request):
    if request.method != "POST":
        raise Http404()

    try:
        tagged = TaggedMaterial.objects.get(id=int(request.POST["id"]))
    except (ValueError, TypeError, TaggedMaterial.DoesNotExist):
        return dict(status="error")

    tagged.delete()
    return dict(status="success")


@ajax_request
def list_standards(request, existing=False):

    if existing:
        qs = TaggedMaterial.objects.all().values_list(
            "tag__standard__id", "tag__standard__name"
        ).order_by("tag__standard__id").distinct()
    else:
        qs = AlignmentTag.objects.all().values_list(
            "standard__id", "standard__name"
        ).order_by("standard__id").distinct()

    return dict(options=list(dict(id=id, name=name) for id, name in qs))


def cmp_grades(grade1, grade2):
    # Sort grades in the following order:
    # K
    # 1
    # 2
    # 3
    # 4
    # 5
    # 6
    # 7
    # 8
    # 6-8
    # 9-10
    # 11-12
    # K-12

    # grade1 and grade2 are actually tuples:
    # (start_grade_code, start_grade_order, start_grade_name,
    #  end_grade_code, end_grade_order, end_grade_name).
    # end_grade_* values may be None.

    # Sort by end_grade order. If it's empty use start_grade order.
    r = cmp(
        grade1[4] if grade1[4] is not None else grade1[1],
        grade2[4] if grade2[4] is not None else grade2[1],
    )

    if not r:
        # If end_grade's order are equal sort by start_grade order in reverse order
        r = -cmp(grade1[1], grade2[1])

    return r


@ajax_request
def list_grades(request, existing=False):
    standard = request.POST.get("standard")
    try:
        standard = Standard.objects.get(id=int(standard))
    except (ValueError, TypeError, Standard.DoesNotExist):
        return HttpResponseBadRequest()

    if existing:
        qs = TaggedMaterial.objects.filter(
            tag__standard=standard
        ).values_list("tag__grade__code", "tag__grade__order", "tag__grade__name",
                      "tag__end_grade__code", "tag__end_grade__order", "tag__end_grade__name").order_by().distinct()
    else:
        qs = AlignmentTag.objects.filter(
            standard=standard
        ).values_list("grade__code", "grade__order", "grade__name",
                      "end_grade__code", "end_grade__order", "end_grade__name").order_by().distinct()

    grades = list(qs)
    grades.sort(cmp=cmp_grades)

    grades = list(
        dict(
            id="%s-%s" % (start_code, end_code) if end_code else start_code,
            name="%s-%s Grades" % (start_code, end_code) if end_code else start_name,
        ) for start_code, start_order, start_name,
              end_code, end_order, end_name in grades)

    return dict(options=grades)


@ajax_request
def list_categories(request, existing=False):
    standard = request.POST.get("standard")
    try:
        standard = Standard.objects.get(id=int(standard))
    except (ValueError, TypeError, Standard.DoesNotExist):
        return HttpResponseBadRequest()

    grade = request.POST.get("grade")
    if "-" in grade:
        grade, end_grade = grade.split("-")
    else:
        end_grade = None
    try:
        grade = Grade.objects.get(code=grade)
        if end_grade:
            end_grade = Grade.objects.get(code=end_grade)
    except (ValueError, TypeError, Grade.DoesNotExist):
        return HttpResponseBadRequest()

    if existing:
        qs = TaggedMaterial.objects.filter(
            tag__standard=standard, tag__grade=grade,
            tag__end_grade=end_grade,
        ).values_list(
            "tag__category__id", "tag__category__name"
        ).order_by("tag__category__id").distinct()
    else:
        qs = AlignmentTag.objects.filter(
            standard=standard, grade=grade, end_grade=end_grade,
        ).values_list(
            "category__id", "category__name"
        ).order_by("category__id").distinct()

    return dict(options=list(dict(id=id, name=name) for id, name in qs))


TAG_CODE_RE = re.compile(r"(.+)?\.(\d+)(?:\.?[a-z])?$")


def cmp_tags(tag1, tag2):
    tag1 = tag1["full_code"]
    tag2 = tag2["full_code"]

    tag1_prefix, tag1_digit = TAG_CODE_RE.search(tag1).groups()
    tag2_prefix, tag2_digit = TAG_CODE_RE.search(tag2).groups()

    if tag1_prefix == tag2_prefix and tag1_digit != tag2_digit:
        return cmp(int(tag1_digit), int(tag2_digit))

    return cmp(tag1, tag2)


@ajax_request
def list_tags(request, existing=False):
    standard = request.POST.get("standard")
    try:
        standard = Standard.objects.get(id=int(standard))
    except (ValueError, TypeError, Standard.DoesNotExist):
        return HttpResponseBadRequest()

    grade = request.POST.get("grade")
    if "-" in grade:
        grade, end_grade = grade.split("-")
    else:
        end_grade = None
    try:
        grade = Grade.objects.get(code=grade)
        if end_grade:
            end_grade = Grade.objects.get(code=end_grade)
    except (ValueError, TypeError, Grade.DoesNotExist):
        return HttpResponseBadRequest()

    category = request.POST.get("category")
    try:
        category = LearningObjectiveCategory.objects.get(id=int(category))
    except (ValueError, TypeError, LearningObjectiveCategory.DoesNotExist):
        return HttpResponseBadRequest()

    if existing:
        tags = set(
            tagged.tag for tagged in TaggedMaterial.objects.filter(
                tag__standard=standard,
                tag__grade=grade,
                tag__end_grade=end_grade,
                tag__category=category
            ).select_related()
        )
    else:
        tags = AlignmentTag.objects.filter(
            standard=standard,
            grade=grade,
            end_grade=end_grade,
            category=category
        )

    tags = list(dict(id=t.id, name=unicode(t), subcategory=t.subcategory, full_code=t.full_code) for t in tags)

    tags.sort(cmp=cmp_tags)

    # Group tag by subcategory and create the following structure:
    # tag1.subcategory
    # - tag1
    # - tag2 (has the same subcat as tag1)
    # - tag3 (has the same subcat as tag2)
    # tag4.subcategory
    # - tag4
    # - tag5 (has the same subcat as tag4)
    # ....
    subcategories = []
    items = []
    name = None

    for tag in tags:
        if tag["subcategory"] != name:
            # Start filling the next optgroup
            if name and items:
                subcategories.append(dict(name=truncatechars(name.rstrip("."), 90), items=items))
            name = tag["subcategory"]
            items = []
        items.append(dict(id=tag["id"],
                          name=tag["name"],
                          code=tag["full_code"]))

    if name and items:
        # Add the last subcategory to final results
        subcategories.append(dict(name=truncatechars(name.rstrip("."), 90), items=items))

    # Return data organized as simple dropdown. This allows to select
    # subcategory (used on advanced search page).
    if "no-optgroups" in request.REQUEST:
        options = []
        for subcat in subcategories:
            code = "cluster:" + subcat["items"][0]["code"]
            options.append(dict(
                id=code,
                code=code,
                name=subcat["name"],
            ))
            for item in subcat["items"]:
                item["name"] = "&#160;" * 4 + item["name"]
                options.append(item)

        return dict(options=options)

    # Return data organized as optgroups (used in align resource widget).
    else:
        return dict(optgroups=subcategories)


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
            object_id = int(object_id)
            content_type = get_object_or_404(ContentType, id=content_type_id)

            data["evaluations_number"] = Evaluation.objects.filter(
                content_type=content_type,
                object_id=object_id,
                confirmed=True,
            ).count()

            scores = StandardAlignmentScore.objects.filter(
                alignment_tag=tag,
                evaluation__content_type=content_type,
                evaluation__object_id=object_id,
            )
            if scores.exists():
                value = scores.aggregate(value=Avg("score__value"))["value"]
                data["score_value"] = value
                if value is None:
                    data["score_class"] = "na"
                else:
                    value = int(round(value))
                    data["score_class"] = str(value)
                data["score_verbose"] = get_verbose_score_name(value)
            else:
                data["score_value"] = None
                data["score_verbose"] = u"Not Rated"
                data["score_class"] = "nr"

        return data
