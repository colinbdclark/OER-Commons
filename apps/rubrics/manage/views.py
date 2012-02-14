from annoying.decorators import ajax_request
from annoying.functions import get_object_or_None
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
from django.views.generic import TemplateView, FormView, View
from materials.models import Course, Library, CommunityItem, GenericMaterial, GradeLevel, GeneralSubject
from rubrics.models import StandardAlignmentScore, RubricScore, Rubric, \
    Evaluation, RubricScoreValue, get_verbose_score_name
from users.views.login import LoginForm
from operator import or_
import datetime
import calendar
from core.search import reindex


class Login(FormView):

    template_name = "rubrics/manage/login.html"
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        request.session.set_test_cookie()
        return super(Login, self).get(request, *args, **kwargs)

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


def evaluator_name(first_name, last_name, email, username):
    if first_name and last_name:
        return "%s %s" % (first_name, last_name)
    elif email:
        return email
    return username


RUBRICS_SHORT_NAMES = {
    0: u"1 Alignment",
    1: u"2 Explanation",
    2: u"3 Materials",
    3: u"4 Assessments",
    4: u"5 Interactivity",
    5: u"6 Practice Exercises",
    6: u"7 Deeper Learning",
}


class ManageRubricsMixin(object):

    page_title = None

    def get_breadcrumbs(self):
        return getattr(self, "breadcrumbs", [])

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
        breadcrumbs = self.get_breadcrumbs()
        if breadcrumbs:
            data["breadcrumbs"] = [dict(url=reverse("rubrics_manage:index"),
                                        name="Manage Evaluations")] + breadcrumbs
        return data


class Index(ManageRubricsMixin, TemplateView):

    template_name = "rubrics/manage/index.html"
    page_title = u"Manage Evaluations"

    def get_breadcrumbs(self):
        if self.rubric_name:
            return [dict(name="Rubric: %s" % self.rubric_name)]
        return []

    def dispatch(self, request, *args, **kwargs):
        #noinspection PyArgumentEqualDefault
        self.rubric_id = kwargs.pop("rubric_id", None)
        self.rubric_name = None
        if self.rubric_id is not None:
            self.rubric_id = int(self.rubric_id)
            #noinspection PySimplifyBooleanCheck
            if self.rubric_id == 0:
                self.rubric_name = u"Degree of Alignment"
            else:
                self.rubric_name = get_object_or_404(Rubric, id=self.rubric_id).name
        return super(Index, self).dispatch(request, *args, **kwargs)

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

        if self.rubric_id is not None:
            #noinspection PySimplifyBooleanCheck
            if self.rubric_id == 0:
                evaluations_ids = StandardAlignmentScore.objects.exclude(
                    score__value=None
                ).values_list(
                    "evaluation__id",
                    flat=True,
                ).distinct()
            else:
                evaluations_ids = RubricScore.objects.exclude(
                    score__value=None
                ).filter(
                    rubric__id=self.rubric_id
                ).values_list("evaluation__id", flat=True)

            qs = qs.filter(id__in=evaluations_ids)

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

        grade_level = request.POST.get("grade_level")
        if grade_level:
            grade_level = get_object_or_None(GradeLevel, id=int(grade_level))

        general_subject = request.POST.get("general_subject")
        if general_subject:
            general_subject = get_object_or_None(GeneralSubject, id=int(general_subject))

        for content_type_id, object_ids in evaluated_resources_dict.items():
            model = ContentType.objects.get(id=content_type_id).model_class()
            qs = model.objects.filter(id__in=object_ids)
            if model in (Course, Library):
                fields = ["slug", "title", "url", "institution__name"]
            elif model == CommunityItem:
                fields = ["slug", "title", "url"]
            elif model == GenericMaterial:
                fields = ["url"]
            else:
                continue

            if grade_level:
                if not hasattr(model, "grade_levels"):
                    continue
                qs = qs.filter(grade_levels=grade_level)

            if general_subject:
                if not hasattr(model, "general_subjects"):
                    continue
                qs = qs.filter(general_subjects=general_subject)

            if search:
                qs = qs.filter(reduce(or_, map(lambda f: models.Q(**{f+"__icontains":search}), fields)))

            qs = qs.values("id", *fields)

            for row in qs:
                object_id = row.pop("id")
                data = dict(
                    total_evaluations=0, title=u"", url=u"", oer_url=u"",
                    institution__name=u"", hostname=u"", last_evaluated=None,
                    evaluator=u"", comments=False,
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

                slug = row.pop("slug", None)
                if slug:
                    data["oer_url"] = reverse("materials:%s:view_item" % model.namespace,
                                              kwargs=dict(slug=slug))
                data.update(row)
                items[(content_type_id, object_id)] = data

        qs = Evaluation.objects.filter(confirmed=True)
        if from_date:
            qs = qs.filter(timestamp__gte=from_date)
        if until_date:
            qs = qs.filter(timestamp__lte=until_date)

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
            "user__first_name",
            "user__last_name",
            "user__email",
            "user__username",
            "user__id",
        )

        for content_type_id, object_id, hostname, timestamp, first_name, last_name, email, username, user_id in qs:
            k = (content_type_id, object_id)
            if k in items and items[k]["last_evaluated"] is None:
                items[k].update(dict(
                    last_evaluated=timestamp,
                    hostname=hostname,
                    evaluator=evaluator_name(first_name, last_name, email, username),
                    manage_user_url=reverse("rubrics_manage:user",
                        kwargs=dict(user_id=user_id)
                    )
                ))

        for model in (StandardAlignmentScore, RubricScore):
            qs = model.objects.filter(
                evaluation__confirmed=True,
            ).exclude(comment=u"").values_list(
                "evaluation__content_type__id",
                "evaluation__object_id",
            ).distinct()
            for k in qs:
                if k in items:
                    items[k]["comments"] = True

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

        if self.rubric_id is None:
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
        else:
            #noinspection PySimplifyBooleanCheck
            if self.rubric_id == 0:
                scores = StandardAlignmentScore.objects.exclude(
                    score__value=None
                )
            else:
                scores = RubricScore.objects.filter(
                    rubric__id=self.rubric_id
                ).exclude(score__value=None)

            data["mean_score"] = scores.aggregate(
                models.Avg("score__value")
            )["score__value__avg"]

            evaluations = Evaluation.objects.filter(
                confirmed=True,
                id__in=scores.values_list("evaluation__id", flat=True)
            )
            data["total_evaluations"] = evaluations.count()
            data["week_evaluations"] = evaluations.filter(
                timestamp__gte=week_start_date
            ).count()

        data["grade_levels"] = GradeLevel.objects.values("id", "name")
        data["general_subjects"] = GeneralSubject.objects.values("id", "name")
        data["rubrics"] = [dict(id=0, name=RUBRICS_SHORT_NAMES[0])] + map(
            lambda id: dict(id=id, name=RUBRICS_SHORT_NAMES[id]),
            Rubric.objects.values_list("id", flat=True)
        )
        data["rubric_id"] = self.rubric_id
        data["rubric"] = self.rubric_name

        return data


class ResourceEvaluations(ManageRubricsMixin, TemplateView):

    template_name = "rubrics/manage/resource.html"
    breadcrumbs = [dict(name="Resource Evaluations")]

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

        standard_scores = StandardAlignmentScore.objects.filter(
            evaluation__confirmed=True,
            evaluation__content_type=self.content_type,
            evaluation__object_id=self.object.id,
        )
        data["average_scores"].append(dict(
            rubric=u"R1",
            score=standard_scores.exclude(score__value=None).aggregate(
                models.Avg("score__value")
            )["score__value__avg"]
        ))

        rubric_scores = RubricScore.objects.filter(
            evaluation__confirmed=True,
            evaluation__content_type=self.content_type,
            evaluation__object_id=self.object.id
        )
        for i, rubric_id in enumerate(Rubric.objects.values_list("id", flat=True)):
            data["average_scores"].append(dict(
                rubric=u"R%i" % (i + 2),
                score=rubric_scores.filter(
                    rubric__id=rubric_id
                ).exclude(score__value=None).aggregate(
                    models.Avg("score__value")
                )["score__value__avg"]
            ))

        comments = []
        for qs in (standard_scores, rubric_scores):
            for score in qs.exclude(comment="").select_related():
                comment = dict(
                    text=score.comment,
                    timestamp=score.evaluation.timestamp,
                    author=score.evaluation.user,
                )

                if isinstance(score, StandardAlignmentScore):
                    title = u"Degree of Alignment to %s" % score.alignment_tag.full_code
                else:
                    title = score.rubric.name

                #noinspection PyUnresolvedReferences
                comment["title"] = u"%s: %s (%s)" % (
                    title,
                    get_verbose_score_name(score.score.value),
                    score.score.get_value_display(),
                )

                comments.append(comment)
        data["comments"] = comments

        return data

    #noinspection PyUnusedLocal
    @method_decorator(ajax_request)
    def post(self, request, *args, **kwargs):

        items = {}
        for row in Evaluation.objects.filter(
            confirmed=True,
            content_type=self.content_type,
            object_id=self.object.id,
        ).values("id",
                 "hostname",
                 "timestamp",
                 "user__id",
                 "user__first_name",
                 "user__last_name",
                 "user__email",
                 "user__username",
                 "ip"):
            id = row["id"]
            user_id = row.pop("user__id")
            row["evaluator"] = evaluator_name(
                row.pop("user__first_name"),
                row.pop("user__last_name"),
                row.pop("user__email"),
                row.pop("user__username"),
            )
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
    breadcrumbs = [dict(name="Evaluations by User")]

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
            "id",
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
            else:
                data["average"] = None


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


class DeleteEvaluation(ManageRubricsMixin, View):

    #noinspection PyUnusedLocal
    @method_decorator(ajax_request)
    def post(self, request, *args, **kwargs):

        result = dict(status="error")
        try:
            id = int(request.POST["id"])
        except (KeyError, ValueError, TypeError):
            return result

        evaluation = get_object_or_None(Evaluation, id=id)
        if not evaluation:
            return result

        object = evaluation.content_object
        evaluation.delete()
        reindex(object)
        result["status"] = "success"

        return result


class EditEvaluation(ManageRubricsMixin, View):

    #noinspection PyUnusedLocal
    @method_decorator(ajax_request)
    def post(self, request, *args, **kwargs):

        result = dict(status="error")
        try:
            id = int(request.POST["id"])
        except (KeyError, ValueError, TypeError):
            return result

        evaluation = get_object_or_None(Evaluation, id=id)

        if not evaluation:
            return result

        data = []
        for rubric in Rubric.objects.all():
            #noinspection PyTypeChecker
            k = "r%i" % (rubric.id + 1)

            if k in request.POST:
                value = request.POST[k].strip() or None

                if value is not None:
                    try:
                        value = int(value)
                    except (TypeError, ValueError):
                        continue

                value = get_object_or_None(
                    RubricScoreValue,
                    rubric=rubric,
                    value=value
                )

                if not value:
                    continue

                data.append((rubric, value))

        if not data:
            return result

        object = evaluation.content_object

        for rubric, value in data:
            score = get_object_or_None(
                RubricScore,
                evaluation=evaluation,
                rubric=rubric
            )

            if score:
                score.score = value
                score.save()
            else:
                RubricScore.objects.create(
                    evaluation=evaluation,
                    rubric=rubric,
                    score=value,
                )

        reindex(object)
        result["status"] = "success"

        return result
