from annoying.decorators import ajax_request
from django.contrib.auth import login
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import redirect
from django.template.defaultfilters import floatformat
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView
from materials.models import Course, Library, CommunityItem, GenericMaterial
from rubrics.models import StandardAlignmentScore, RubricScore, Rubric
from users.views.login import LoginForm


class Login(FormView):

    template_name = "rubrics/manage/login.html"
    form_class = LoginForm

    def get_form_kwargs(self):
        kwargs = super(Login, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        login(self.request, form.get_user())
        return redirect("rubrics_manage:index")

    def get_context_data(self, **kwargs):
        data = super(Login, self).get_context_data(**kwargs)
        data["page_title"] = u"Log in"
        return data


class ManageRubricsMixin(object):

    page_title = None

    def get_page_title(self):
        return self.page_title

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated():
            return redirect("rubrics_manage:login")
        elif not user.has_perm("rubrics.can_manage") and not user.is_superuser:
            return redirect("rubrics_manage:login")

        return super(ManageRubricsMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(ManageRubricsMixin, self).get_context_data(**kwargs)
        data["page_title"] = self.get_page_title()
        return data


class Index(ManageRubricsMixin, TemplateView):

    template_name = "rubrics/manage/index.html"
    page_title = u"Manage Evaluations"

    @method_decorator(ajax_request)
    def post(self, request, *args, **kwargs):

        evaluated_resources = set(
            StandardAlignmentScore.objects.filter(
                confirmed=True
            ).values_list(
                "content_type__id",
                "object_id",
            )
        ) | set(
                RubricScore.objects.filter(
                confirmed=True
            ).values_list(
                "content_type__id",
                "object_id",
            )
        )

        evaluated_resources_dict = {}
        for content_type_id, object_id in evaluated_resources:
            if content_type_id not in evaluated_resources_dict:
                evaluated_resources_dict[content_type_id] = [object_id]
            else:
                evaluated_resources_dict[content_type_id].append(object_id)

        items = {}

        for content_type_id, object_ids in evaluated_resources_dict.items():
            model = ContentType.objects.get(id=content_type_id).model_class()
            qs = model.objects.filter(id__in=object_ids)
            if model in (Course, Library):
                fields = ["title", "url", "institution__name"]
            elif model == CommunityItem:
                fields = ["title", "url"]
            elif model == GenericMaterial:
                fields = ["url"]
            else:
                continue

            for row in model.objects.filter(id__in=object_ids).values("id", *fields):
                object_id = row.pop("id")
                data = dict(
                    r1=None, r2=None, r3=None, r4=None, r5=None, r6=None, r7=None,
                    title=u"", url=u"", institution__name=u""
                )
                data.update(row)
                items[(content_type_id, object_id)] = data


        qs = StandardAlignmentScore.objects.filter(confirmed=True).exclude(
            score__value=None).values("content_type__id", "object_id"
        ).annotate(average_score=models.Avg("score__value"))
        for row in qs:
            k = (row["content_type__id"], row["object_id"])
            if k not in items:
                continue
            items[k]["r1"] = row["average_score"]

        for i, rubric_id in enumerate(Rubric.objects.values_list("id", flat=True)):
            qs = RubricScore.objects.filter(
                confirmed=True, rubric__id=rubric_id
            ).exclude(score__value=None).values(
                "content_type__id", "object_id"
            ).annotate(
                average_score=models.Avg("score__value")
            )
            for row in qs:
                k = (row["content_type__id"], row["object_id"])
                if k not in items:
                    continue
                items[k]["r%i" % (i + 2)] = row["average_score"]

        items = items.values()

        if "sort" in request.POST:
            sort_on = request.POST["sort"]
            items.sort(key=lambda x: x[sort_on], reverse=request.POST.get("order") == "desc")

        page = int(request.POST.get("page", "1"))
        batch_size = int(request.POST.get("rows", "10"))

        paginator = Paginator(items, batch_size)

        items = paginator.page(page).object_list

        for item in items:
            for k, v in item.items():
                if k.startswith("r") and len(k) == 2:
                    if v is None:
                        item[k] = u""
                    else:
                        item[k] = floatformat(v)

        return dict(
            total=paginator.count,
            rows=paginator.page(page).object_list
        )
