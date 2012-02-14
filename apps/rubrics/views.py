from annoying.decorators import ajax_request
from annoying.functions import get_object_or_None
from curriculum.models import AlignmentTag
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Avg
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View
from materials.models import Course, Library, CommunityItem, GenericMaterial
from rubrics.models import Rubric, StandardAlignmentScoreValue, \
    StandardAlignmentScore, RubricScore, RubricScoreValue, Evaluation
from utils.decorators import login_required
import urlparse
from core.search import reindex


HOSTNAME_COOKIE = "evaluation_tool_hostname"


class Intro(TemplateView):

    template_name = "rubrics/tool/intro.html"

    def get(self, request, *args, **kwargs):
        self.url = request.GET.get("url", u"").strip()
        if not self.url:
            return HttpResponseBadRequest()

        for model in (Course, Library, CommunityItem, GenericMaterial):
            self.object = get_object_or_None(model, url=self.url)
            if self.object:
                break

        if not self.object and self.request.user.is_authenticated():
            self.object = GenericMaterial.objects.create(
                url=self.url,
                creator=self.request.user,
            )

        from_url = request.GET.get("from", u"").strip()
        if from_url:
            hostname = urlparse.urlparse(from_url).hostname or u""
        else:
            hostname = u""

        response = super(Intro, self).get(request, *args, **kwargs)
        response.set_cookie(HOSTNAME_COOKIE, hostname)

        return response

    def get_context_data(self, **kwargs):
        data = super(Intro, self).get_context_data(**kwargs)
        data["url"] = self.url
        data["object"] = self.object
        if self.object:
            data["content_type"] = ContentType.objects.get_for_model(self.object)
        return data


class EvaluateViewMixin(object):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        content_type_id = kwargs.pop("content_type_id")
        self.content_type = get_object_or_404(ContentType, id=int(content_type_id))
        object_id = kwargs.pop("object_id")
        model = self.content_type.model_class()
        self.object = get_object_or_404(model, id=int(object_id))
        self.enable_alignment_scores = Evaluation.enable_alignment_scores(self.object)
        print self.enable_alignment_scores
        #noinspection PyUnresolvedReferences
        return super(EvaluateViewMixin, self).dispatch(request, *args, **kwargs)


class Rubrics(EvaluateViewMixin, TemplateView):

    template_name = "rubrics/tool/rubrics.html"

    def get_context_data(self, **kwargs):
        data = super(Rubrics, self).get_context_data(**kwargs)
        data["content_type"] = self.content_type
        data["object"] = self.object
        data["enable_alignment_scores"] = self.enable_alignment_scores
        if isinstance(self.object, (Course, Library, CommunityItem)):
            data["toolbar_view_url"] = reverse(
                "materials:%s:toolbar_view_item" % self.object.namespace,
                kwargs=dict(slug=self.object.slug),
            )

        evaluation = Evaluation.objects.get_or_create(
            content_type=self.content_type,
            object_id=self.object.id,
            user=self.request.user,
        )[0]

        evaluation.ip = self.request.META["REMOTE_ADDR"]
        evaluation.hostname = self.request.COOKIES.get(HOSTNAME_COOKIE, u"")
        evaluation.save()

        if self.enable_alignment_scores:
            tags = AlignmentTag.objects.filter(
                id__in=self.object.alignment_tags.values_list("tag__id",
                                                              flat=True).distinct()
            )
            data["alignment_tags"] = []
            for tag in tags:
                score = get_object_or_None(
                    StandardAlignmentScore,
                    evaluation=evaluation,
                    alignment_tag=tag,
                )
                if score:
                    tag.score_value = score.score
                    tag.scored = True
                    tag.comment = score.comment
                else:
                    tag.score_value = None
                    tag.scored = False
                    tag.comment = u""
                data["alignment_tags"].append(tag)

            data["alignment_scored"] = data["alignment_tags"] and all(map(lambda x: x.score_value, data["alignment_tags"]))
            data["alignment_score_values"] = StandardAlignmentScoreValue.objects.all()

        data["rubrics"] = []
        for rubric in Rubric.objects.all():
            score = get_object_or_None(
                RubricScore,
                evaluation=evaluation,
                rubric=rubric,
            )
            if score:
                rubric.score_value = score.score
                rubric.scored = True
                rubric.comment = score.comment
            else:
                rubric.score_value = None
                rubric.scored = False
                rubric.comment = u""
            data["rubrics"].append(rubric)

        return data

    #noinspection PyUnusedLocal
    @method_decorator(ajax_request)
    def post(self, request, *args, **kwargs):

        evaluation = get_object_or_None(
            Evaluation,
            content_type=self.content_type,
            object_id=self.object.id,
            user=request.user,
        )
        if not evaluation:
            return HttpResponseBadRequest()

        delete = "delete" in request.POST
        score_value_id = None

        if not delete:
            score_value_id = request.POST.get("score_id")
            try:
                score_value_id = int(score_value_id)
            except (TypeError, ValueError):
                return HttpResponseBadRequest()

        tag_id = request.POST.get("tag_id")
        rubric_id = request.POST.get("rubric_id")
        comment = request.POST.get("comment", u"").strip()

        if self.enable_alignment_scores and tag_id:
            try:
                tag_id = int(tag_id)
            except (TypeError, ValueError):
                return HttpResponseBadRequest()

            tag = get_object_or_None(AlignmentTag, id=tag_id)
            if not tag:
                return HttpResponseBadRequest()

            if delete:
                StandardAlignmentScore.objects.filter(
                    evaluation=evaluation,
                    alignment_tag=tag,
                ).delete()
            else:
                score_value = get_object_or_None(StandardAlignmentScoreValue,
                                                 id=score_value_id)
                if not score_value:
                    return HttpResponseBadRequest()

                score, created = StandardAlignmentScore.objects.get_or_create(
                    evaluation=evaluation,
                    alignment_tag=tag,
                    defaults=dict(score=score_value, comment=comment)
                )
                if not created:
                    score.score = score_value
                    score.comment = comment
                    score.save()

        if rubric_id:
            try:
                rubric_id = int(rubric_id)
            except (TypeError, ValueError):
                return HttpResponseBadRequest()
            rubric = get_object_or_None(Rubric, id=rubric_id)
            if not rubric:
                return HttpResponseBadRequest()

            if delete:
                RubricScore.objects.filter(
                    evaluation=evaluation,
                    rubric=rubric
                ).delete()
            else:
                score_value = get_object_or_None(RubricScoreValue,
                                                 id=score_value_id)
                if not score_value:
                    return HttpResponseBadRequest()

                score, created = RubricScore.objects.get_or_create(
                    evaluation=evaluation,
                    rubric=rubric,
                    defaults=dict(score=score_value, comment=comment)
                )
                if not created:
                    score.score = score_value
                    score.comment = comment
                    score.save()

        evaluation.confirmed = False
        evaluation.save()

        reindex(self.object)

        return dict(status="success")


class Results(EvaluateViewMixin, TemplateView):

    template_name = "rubrics/tool/results.html"

    def get_context_data(self, **kwargs):

        data = super(Results, self).get_context_data(**kwargs)
        data["content_type"] = self.content_type
        data["object"] = self.object
        data["enable_alignment_scores"] = self.enable_alignment_scores
        data["scores"] = []

        evaluation = get_object_or_None(
            Evaluation,
            content_type=self.content_type,
            object_id=self.object.id,
            user=self.request.user,
        )

        if not evaluation:
            return redirect("rubrics:evaluate_rubrics",
                            kwargs=dict(
                                content_type_id=self.content_type.id,
                                object_id=self.object.id,
                            ))

        data["finalized"] = evaluation.confirmed

        not_scored_tags = []
        if self.enable_alignment_scores:
            alignment_scores = StandardAlignmentScore.objects.filter(
                evaluation__content_type=self.content_type,
                evaluation__object_id=self.object.id,
            )

            tags = AlignmentTag.objects.filter(
                id__in=self.object.alignment_tags.values_list("tag__id",
                                                              flat=True).distinct()
            )

            data["tags"] = []

            for tag in tags:
                tag_scores = alignment_scores.filter(alignment_tag__id=tag.id)
                average_score = tag_scores.aggregate(Avg("score__value"))["score__value__avg"]

                if not tag_scores.exists():
                    average_score_class = "nr"
                elif average_score is None:
                    average_score_class = None
                else:
                    average_score_class = int(round(average_score))

                user_score_value = None
                comment = None

                try:
                    user_tag_score = tag_scores.get(
                        evaluation=evaluation
                    )
                    user_score_value = user_tag_score.score.value
                    if user_score_value is None:
                        user_score_class = None
                    else:
                        user_score_class = int(round(user_score_value))
                    comment = user_tag_score.comment
                except StandardAlignmentScore.DoesNotExist:
                    user_score_class = "nr"


                data["tags"].append(dict(
                    name=tag.full_code,
                    user_score=user_score_value,
                    user_score_class=user_score_class,
                    average_score=average_score,
                    average_score_class=average_score_class,
                    comment=comment,
                ))

            not_scored_tags = set(tags.values_list("id", flat=True)) - \
                              set(alignment_scores.filter(evaluation=evaluation
                              ).values_list("alignment_tag__id", flat=True))

        rubrics = Rubric.objects.all()
        rubric_scores = RubricScore.objects.filter(
            evaluation__content_type=self.content_type,
            evaluation__object_id=self.object.id,
        )
        for rubric in rubrics:
            scores = rubric_scores.filter(rubric=rubric)
            user_score = scores.filter(evaluation__user=self.request.user)

            if not user_score.exists():
                user_score = None
                user_score_class = "nr"
                comment = None
            else:
                user_score, comment = user_score.values_list(
                    "score__value",
                    "comment"
                )[0]
                user_score_class = user_score

            average_score = scores.aggregate(
                Avg("score__value")
            )["score__value__avg"]

            if not scores.exists():
                average_score_class = "nr"
            elif average_score is None:
                average_score_class = None
            else:
                average_score_class = int(round(average_score))

            data["scores"].append(dict(
                name=rubric.name,
                user_score=user_score,
                user_score_class=user_score_class,
                average_score=average_score,
                average_score_class=average_score_class,
                comment=comment,
            ))

        not_scored_section = None
        user_rubric_scores = rubric_scores.filter(
            evaluation__user=self.request.user
        )
        not_scored_rubrics = set(rubrics.values_list("id", flat=True)) - \
                             set(user_rubric_scores.values_list("rubric__id",
                                                                flat=True))
        if not_scored_tags:
            not_scored_section = "standard%i" % sorted(not_scored_tags)[0]
        elif not_scored_rubrics:
            not_scored_section = "rubric%i" % sorted(not_scored_rubrics)[0]

        data["not_scored_section"] = not_scored_section

        return data


class Finalize(EvaluateViewMixin, View):

    #noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):

        evaluation = get_object_or_None(
            Evaluation,
            content_type=self.content_type,
            object_id=self.object.id,
            user=self.request.user,
        )

        if not evaluation:
            return redirect("rubrics:evaluate_rubrics",
                            kwargs=dict(
                                content_type_id=self.content_type.id,
                                object_id=self.object.id,
                            ))

        evaluation.confirmed = True
        evaluation.save()

        reindex(self.object)

        return redirect("rubrics:evaluate_results",
            content_type_id=self.content_type.id,
            object_id=self.object.id,
        )


class Align(EvaluateViewMixin, TemplateView):

    template_name = "rubrics/tool/align.html"

    def get_context_data(self, **kwargs):
        data = super(Align, self).get_context_data(**kwargs)
        data["action"] = reverse("curriculum:align",
            args=(
                self.content_type.app_label,
                self.content_type.model,
                self.object.id,
            )
        )
        data["content_type"] = self.content_type
        data["object"] = self.object
        return data
