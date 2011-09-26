from annoying.decorators import ajax_request
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db import models
from django.shortcuts import redirect, get_object_or_404
from django.template.defaultfilters import floatformat
from django.utils.dateformat import format
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView
from materials.models import Course, Library, CommunityItem, GenericMaterial
from rubrics.models import StandardAlignmentScore, RubricScore, Rubric, \
    Evaluation
from users.views.login import LoginForm
from operator import or_
import datetime
import calendar


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

        #noinspection PyUnresolvedReferences
        return super(ManageRubricsMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        #noinspection PyUnresolvedReferences
        data = super(ManageRubricsMixin, self).get_context_data(**kwargs)
        data["page_title"] = self.get_page_title()
        return data


class Index(ManageRubricsMixin, TemplateView):

    template_name = "rubrics/manage/index.html"
    page_title = u"Manage Evaluations"

    #noinspection PyUnusedLocal
    @method_decorator(ajax_request)
    def post(self, request, *args, **kwargs):

        search = request.POST.get("search")

        from_date = request.POST.get("from_date")
        if from_date:
            try:
                from_date = datetime.datetime.strptime(from_date, "%m/%d/%Y")
            except ValueError:
                from_date = None

        until_date = request.POST.get("until_date")
        if until_date:
            try:
                until_date = datetime.datetime.strptime(until_date, "%m/%d/%Y") + datetime.timedelta(days=1)
            except ValueError:
                until_date = None

        qs = Evaluation.objects.filter(confirmed=True)
        if from_date:
            qs = qs.filter(timestamp__gte=from_date)
        if until_date:
            qs = qs.filter(timestamp__lte=until_date)

        evaluated_resources = qs.values_list(
                "content_type__id",
                "object_id",
            ).distinct()

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

            if search:
                qs = qs.filter(reduce(or_, map(lambda f: models.Q(**{f+"__icontains":search}), fields)))

            qs = qs.values("id", *fields)

            for row in qs:
                object_id = row.pop("id")
                data = dict(
                    total_evaluations=0, title=u"", url=u"", institution__name=u"",
                    hostname=u"", last_evaluated=None, evaluator=u"", ip=u"",
                    manage_resource_url=reverse("rubrics_manage:resource",
                        kwargs=dict(
                            content_type_id=content_type_id,
                            object_id=object_id,
                        )
                    ),
                    manage_user_url=u"",
                )
                for i in xrange(1, 8):
                    data["r%i" % i] = None

                data.update(row)
                items[(content_type_id, object_id)] = data

        qs = Evaluation.objects.filter(confirmed=True)
        if from_date:
            qs = qs.filter(timestamp__gte=from_date)
        if until_date:
            qs = qs.filter(timestamp__lte=until_date)

        qs = qs.values(
                "content_type__id",
                "object_id",
            ).annotate(evaluations_count=models.Count("id")).distinct()
        for row in qs:
            k = (row["content_type__id"],
                 row["object_id"])
            if k in items:
                items[k]["total_evaluations"] = row["evaluations_count"]


        qs = StandardAlignmentScore.objects.filter(evaluation__confirmed=True)
        if from_date:
            qs = qs.filter(evaluation__timestamp__gte=from_date)
        if until_date:
            qs = qs.filter(evaluation__timestamp__lte=until_date)

        qs = qs.exclude(score__value=None).values(
            "evaluation__content_type__id", "evaluation__object_id"
        ).annotate(average_score=models.Avg("score__value"))
        for row in qs:
            k = (row["evaluation__content_type__id"],
                 row["evaluation__object_id"])
            if k not in items:
                continue
            items[k]["r1"] = row["average_score"]


        for i, rubric_id in enumerate(Rubric.objects.values_list("id", flat=True)):
            qs = RubricScore.objects.filter(evaluation__confirmed=True,
                                            rubric__id=rubric_id)
            if from_date:
                qs = qs.filter(evaluation__timestamp__gte=from_date)
            if until_date:
                qs = qs.filter(evaluation__timestamp__lte=until_date)

            qs = qs.exclude(score__value=None).values(
                "evaluation__content_type__id", "evaluation__object_id"
            ).annotate(
                average_score=models.Avg("score__value")
            )
            for row in qs:
                k = (row["evaluation__content_type__id"],
                     row["evaluation__object_id"])
                if k not in items:
                    continue
                items[k]["r%i" % (i + 2)] = row["average_score"]

        qs = Evaluation.objects.filter(confirmed=True)
        if from_date:
            qs = qs.filter(timestamp__gte=from_date)
        if until_date:
            qs = qs.filter(timestamp__lte=until_date)
        qs = qs.order_by(
            "content_type__id",
            "object_id",
            "-timestamp",
        ).values_list(
            "content_type__id",
            "object_id",
            "hostname",
            "timestamp",
            "user__username",
            "user__id",
            "ip",
        )

        for content_type_id, object_id, hostname, timestamp, username, user_id, ip in qs:
            k = (content_type_id, object_id)
            if k in items and items[k]["last_evaluated"] is None:
                items[k].update(dict(
                    last_evaluated=timestamp,
                    hostname=hostname,
                    evaluator=username,
                    ip=ip,
                    manage_user_url=reverse("rubrics_manage:user",
                        kwargs=dict(user_id=user_id)
                    )
                ))

        items = items.values()

        if "sort" in request.POST:
            sort_on = request.POST["sort"]
            items.sort(key=lambda x: x[sort_on], reverse=request.POST.get("order") == "desc")

        page = int(request.POST.get("page", "1"))
        batch_size = int(request.POST.get("rows", "10"))

        paginator = Paginator(items, batch_size)

        items = paginator.page(page).object_list

        for item in items:
            for i in xrange(1, 8):
                k = "r%s" % i
                item[k] = floatformat(item[k])
            if item["last_evaluated"] is not None:
                item["last_evaluated"] = format(item["last_evaluated"],
                                                settings.DATETIME_FORMAT)

        return dict(
            total=paginator.count,
            rows=paginator.page(page).object_list
        )


    def get_context_data(self, **kwargs):
        data = super(Index, self).get_context_data(**kwargs)

        today = datetime.date.today()
        cal = calendar.Calendar()

        week_start_date = None
        for week in cal.monthdatescalendar(today.year, today.month):
            if today in week:
                week_start_date = week[0]
                break

        week_evaluations = Evaluation.objects.filter(
            confirmed=True,
            timestamp__gte=week_start_date,
        )
        data["week_evaluations"] = week_evaluations.count()

        week_users = set(week_evaluations.values_list("user__id", flat=True).distinct())
        old_users = set(
            Evaluation.objects.filter(
                confirmed=True,
                timestamp__lt=week_start_date,
            ).values_list("user__id", flat=True).distinct())

        data["week_users"] = len(week_users - old_users)

        return data


class ResourceEvaluations(ManageRubricsMixin, TemplateView):

    template_name = "rubrics/manage/resource.html"

    def dispatch(self, request, *args, **kwargs):
        self.content_type = get_object_or_404(ContentType,
                                              id=int(kwargs["content_type_id"]))
        model = self.content_type.model_class()
        self.object = get_object_or_404(model, id=int(kwargs["object_id"]))
        return super(ResourceEvaluations, self).dispatch(request, *args, **kwargs)

    def get_page_title(self):
        return u"Evaluation for \"%s\"" % unicode(self.object)

    def get_context_data(self, **kwargs):
        data = super(ResourceEvaluations, self).get_context_data(**kwargs)
        data["content_type"] = self.content_type
        data["object"] = self.object

        evaluations = Evaluation.objects.filter(
            confirmed=True,
            content_type=self.content_type,
            object_id=self.object.id,
        )
        data["total_evaluations"] = evaluations.count()

        data["average_scores"] = []
        data["average_scores"].append(dict(
            rubric=u"R1",
            score=StandardAlignmentScore.objects.filter(
                evaluation__confirmed=True,
                evaluation__content_type=self.content_type,
                evaluation__object_id=self.object.id,
            ).exclude(score__value=None).aggregate(
                models.Avg("score__value")
            )["score__value__avg"]
        ))

        for i, rubric_id in enumerate(Rubric.objects.values_list("id", flat=True)):
            data["average_scores"].append(dict(
                rubric=u"R%i" % (i + 2),
                score=RubricScore.objects.filter(
                    evaluation__confirmed=True,
                    evaluation__content_type=self.content_type,
                    evaluation__object_id=self.object.id,
                    rubric__id=rubric_id,
                ).exclude(score__value=None).aggregate(
                    models.Avg("score__value")
                )["score__value__avg"]
            ))

        return data

    #noinspection PyUnusedLocal
    @method_decorator(ajax_request)
    def post(self, request, *args, **kwargs):

        items = {}
        for row in Evaluation.objects.filter(
            confirmed=True,
            content_type=self.content_type,
            object_id=self.object.id,
        ).values("id", "hostname", "timestamp", "user__id",
                 "user__username", "ip"):
            id = row.pop("id")
            user_id = row.pop("user__id")
            items[id] = row
            for i in xrange(1,8):
                items[id]["r%i" % i] = None
            items[id]["average"] = None
            items[id]["manage_user_url"] = reverse("rubrics_manage:user",
                                                   kwargs=dict(
                                                       user_id=user_id
                                                   ))


        qs = StandardAlignmentScore.objects.filter(
            evaluation__confirmed=True,
            evaluation__content_type=self.content_type,
            evaluation__object_id=self.object.id,
        )

        qs = qs.exclude(score__value=None).values("evaluation__id").annotate(
            average_score=models.Avg("score__value")
        )

        for row in qs:
            k = row["evaluation__id"]
            if k not in items:
                continue
            items[k]["r1"] = row["average_score"]


        for i, rubric_id in enumerate(Rubric.objects.values_list("id", flat=True)):
            qs = RubricScore.objects.filter(
                evaluation__confirmed=True,
                rubric__id=rubric_id,
                evaluation__content_type=self.content_type,
                evaluation__object_id=self.object.id,
            )
            qs = qs.exclude(score__value=None).values("evaluation__id").annotate(
                average_score=models.Avg("score__value")
            )
            for row in qs:
                k = row["evaluation__id"]
                if k not in items:
                    continue
                items[k]["r%i" % (i + 2)] = row["average_score"]

        for data in items.values():
            scores = filter(lambda x: x is not None,
                            map(lambda i: data["r%i" % i], xrange(1, 8)))
            if scores:
                data["average"] = sum(scores) / float(len(scores))


        items = items.values()

        if "sort" in request.POST:
            sort_on = request.POST["sort"]
            items.sort(key=lambda x: x[sort_on], reverse=request.POST.get("order") == "desc")

        page = int(request.POST.get("page", "1"))
        batch_size = int(request.POST.get("rows", "10"))

        paginator = Paginator(items, batch_size)

        items = paginator.page(page).object_list

        for item in items:
            for i in xrange(1, 8):
                k = "r%s" % i
                item[k] = floatformat(item[k])
            if item["timestamp"] is not None:
                item["timestamp"] = format(item["timestamp"],
                                           settings.DATETIME_FORMAT)
            item["average"] = floatformat(item["average"])

        return dict(
            total=paginator.count,
            rows=paginator.page(page).object_list
        )


class UserEvaluations(ManageRubricsMixin, TemplateView):

    template_name = "rubrics/manage/user.html"

    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(User, id=int(kwargs["user_id"]))
        return super(UserEvaluations, self).dispatch(request, *args, **kwargs)

    def get_page_title(self):
        return u"Evaluation by \"%s\"" % unicode(self.user)

    #noinspection PyUnusedLocal
    @method_decorator(ajax_request)
    def post(self, request, *args, **kwargs):

        qs = Evaluation.objects.filter(confirmed=True, user=self.user)

        evaluated_resources = qs.values_list(
                "content_type__id",
                "object_id",
            ).distinct()

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

            qs = qs.values("id", *fields)

            for row in qs:
                object_id = row.pop("id")
                data = dict(
                    title=u"", url=u"", institution__name=u"",
                    hostname=u"", timestamp=None, ip=u"", average_score=None,
                    manage_resource_url=reverse("rubrics_manage:resource",
                        kwargs=dict(
                            content_type_id=content_type_id,
                            object_id=object_id,
                        )
                    )
                )
                for i in xrange(1, 8):
                    data["r%i" % i] = None

                data.update(row)
                items[(content_type_id, object_id)] = data

        qs = StandardAlignmentScore.objects.filter(
            evaluation__confirmed=True,
            evaluation__user=self.user
        )
        qs = qs.exclude(score__value=None).values(
            "evaluation__content_type__id", "evaluation__object_id"
        ).annotate(average_score=models.Avg("score__value"))
        for row in qs:
            k = (row["evaluation__content_type__id"],
                 row["evaluation__object_id"])
            if k not in items:
                continue
            items[k]["r1"] = row["average_score"]

        for i, rubric_id in enumerate(Rubric.objects.values_list("id", flat=True)):
            qs = RubricScore.objects.filter(
                evaluation__confirmed=True,
                rubric__id=rubric_id,
                evaluation__user=self.user
            )
            qs = qs.exclude(score__value=None).values(
                "evaluation__content_type__id", "evaluation__object_id"
            ).annotate(
                average_score=models.Avg("score__value")
            )
            for row in qs:
                k = (row["evaluation__content_type__id"],
                     row["evaluation__object_id"])
                if k not in items:
                    continue
                items[k]["r%i" % (i + 2)] = row["average_score"]

        qs = Evaluation.objects.filter(confirmed=True, user=self.user)
        qs = qs.values(
            "content_type__id",
            "object_id",
            "hostname",
            "timestamp",
            "ip",
        )

        for row in qs:
            k = (row.pop("content_type__id"), row.pop("object_id"))
            items[k].update(row)


        for data in items.values():
            scores = filter(lambda x: x is not None,
                            map(lambda i: data["r%i" % i], xrange(1, 8)))
            if scores:
                data["average"] = sum(scores) / float(len(scores))


        items = items.values()

        if "sort" in request.POST:
            sort_on = request.POST["sort"]
            items.sort(key=lambda x: x[sort_on], reverse=request.POST.get("order") == "desc")

        page = int(request.POST.get("page", "1"))
        batch_size = int(request.POST.get("rows", "10"))

        paginator = Paginator(items, batch_size)

        items = paginator.page(page).object_list

        for item in items:
            for i in xrange(1, 8):
                k = "r%s" % i
                item[k] = floatformat(item[k])
            if item["timestamp"] is not None:
                item["timestamp"] = format(item["timestamp"],
                                           settings.DATETIME_FORMAT)
            item["average"] = floatformat(item["average"])

        return dict(
            total=paginator.count,
            rows=paginator.page(page).object_list
        )

    def get_context_data(self, **kwargs):
        data = super(UserEvaluations, self).get_context_data(**kwargs)
        data["evaluator"] = self.user
        evaluations = Evaluation.objects.filter(
            confirmed=True,
            user=self.user
        )
        data["total_evaluations"] = evaluations.count()
        data["last_evaluated"] = None
        if data["total_evaluations"]:
            data["last_evaluated"] = format(
                evaluations.order_by("-timestamp")[0].timestamp,
                settings.DATE_FORMAT
            )
        return data
