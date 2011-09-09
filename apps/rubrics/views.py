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
from haystack_scheduled.indexes import Indexed
from materials.models import Course, Library, CommunityItem, GenericMaterial
from rubrics.models import Rubric, StandardAlignmentScoreValue, \
    StandardAlignmentScore, RubricScore, RubricScoreValue
from utils.decorators import login_required


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

        return super(Intro, self).get(request, *args, **kwargs)

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
        #noinspection PyUnresolvedReferences
        return super(EvaluateViewMixin, self).dispatch(request, *args, **kwargs)


class Rubrics(EvaluateViewMixin, TemplateView):

    template_name = "rubrics/tool/rubrics.html"

    def get_context_data(self, **kwargs):
        data = super(Rubrics, self).get_context_data(**kwargs)
        data["content_type"] = self.content_type
        data["object"] = self.object
        if isinstance(self.object, (Course, Library, CommunityItem)):
            data["toolbar_view_url"] = reverse(
                "materials:%s:toolbar_view_item" % self.object.namespace,
                kwargs=dict(slug=self.object.slug),
            )

        tags = AlignmentTag.objects.filter(
            id__in=self.object.alignment_tags.values_list("tag__id",
                                                          flat=True).distinct()
        )
        data["alignment_tags"] = []
        for tag in tags:
            score = get_object_or_None(StandardAlignmentScore,
                content_type=self.content_type,
                object_id=self.object.id,
                user=self.request.user,
                alignment_tag=tag
            )
            if score:
                tag.score_value = score.score
                tag.scored = True
            else:
                tag.score_value = None
                tag.scored = False
            data["alignment_tags"].append(tag)
        data["alignment_scored"] = all(map(lambda x: x.score_value, data["alignment_tags"]))

        data["rubrics"] = []
        for rubric in Rubric.objects.all():
            score = get_object_or_None(RubricScore,
                                       content_type=self.content_type,
                                       object_id=self.object.id,
                                       user=self.request.user,
                                       rubric=rubric)
            if score:
                rubric.score_value = score.score
                rubric.scored = True
            else:
                rubric.score_value = None
                rubric.scored = False
            data["rubrics"].append(rubric)

        data["alignment_score_values"] = StandardAlignmentScoreValue.objects.all()
        return data

    #noinspection PyUnusedLocal
    @method_decorator(ajax_request)
    def post(self, request, *args, **kwargs):
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
        if tag_id:
            try:
                tag_id = int(tag_id)
            except (TypeError, ValueError):
                return HttpResponseBadRequest()

            tag = get_object_or_None(AlignmentTag, id=tag_id)
            if not tag:
                return HttpResponseBadRequest()

            if delete:
                StandardAlignmentScore.objects.filter(
                    content_type=self.content_type,
                    object_id=self.object.id,
                    user=request.user,
                    alignment_tag=tag
                ).delete()
            else:
                score_value = get_object_or_None(StandardAlignmentScoreValue,
                                                 id=score_value_id)
                if not score_value:
                    return HttpResponseBadRequest()

                score, created = StandardAlignmentScore.objects.get_or_create(
                    content_type=self.content_type,
                    object_id=self.object.id,
                    user=request.user,
                    alignment_tag=tag,
                    defaults=dict(score=score_value, confirmed=False)
                )
                if not created:
                    score.score = score_value
                    score.confirmed = False
                    score.save()
            return dict(status="success")

        elif rubric_id:
            try:
                rubric_id = int(rubric_id)
            except (TypeError, ValueError):
                return HttpResponseBadRequest()
            rubric = get_object_or_None(Rubric, id=rubric_id)
            if not rubric:
                return HttpResponseBadRequest()

            if delete:
                RubricScore.objects.filter(
                    content_type=self.content_type,
                    object_id=self.object.id,
                    user=request.user,
                    rubric=rubric
                ).delete()
            else:
                score_value = get_object_or_None(RubricScoreValue,
                                                 id=score_value_id)
                if not score_value:
                    return HttpResponseBadRequest()

                score, created = RubricScore.objects.get_or_create(
                    content_type=self.content_type,
                    object_id=self.object.id,
                    user=request.user,
                    rubric=rubric,
                    defaults=dict(score=score_value, confirmed=False)
                )
                if not created:
                    score.score = score_value
                    score.confirmed = False
                    score.save()
            return dict(status="success")

        return HttpResponseBadRequest()


class Results(EvaluateViewMixin, TemplateView):

    template_name = "rubrics/tool/results.html"

    def get_context_data(self, **kwargs):

        data = super(Results, self).get_context_data(**kwargs)
        data["content_type"] = self.content_type
        data["object"] = self.object

        data["scores"] = []

        alignment_scores = StandardAlignmentScore.objects.filter(
            content_type=self.content_type,
            object_id=self.object.id,
        )

        average_score = alignment_scores.aggregate(
            Avg("score__value")
        )["score__value__avg"]
        if average_score is None:
            average_score_class = None
        else:
            average_score_class = int(average_score)

        user_alignment_scores = alignment_scores.filter(
            user=self.request.user
        )

        data["finalized"] = not user_alignment_scores.filter(confirmed=False).exists()

        user_score = user_alignment_scores.aggregate(Avg("score__value"))["score__value__avg"]
        if user_score is None:
            user_score_class = None
        else:
            user_score_class = int(user_score)

        data["scores"].append(dict(
            name=u"Degree of Alignment",
            user_score=user_score,
            user_score_class=user_score_class,
            average_score=average_score,
            average_score_class=average_score_class,
        ))

        tags = AlignmentTag.objects.filter(
            id__in=self.object.alignment_tags.values_list("tag__id",
                                                          flat=True).distinct()
        )

#        for tag in tags:
#            scores = alignment_scores.filter(alignment_tag=tag)
#            user_score=scores.filter(user=self.request.user)
#
#            if not user_score.exists():
#                user_score = None
#            else:
#                user_score = user_score.values_list("score__value",
#                                                    flat=True)[0]
#            average_score =scores.aggregate(
#                Avg("score__value")
#            )["score__value__avg"]
#
#            if average_score is None:
#                average_score_class = None
#            else:
#                average_score_class = int(average_score)
#
#            data["scores"].append(dict(
#                name=tag.full_code,
#                user_score=user_score,
#                average_score=average_score,
#                average_score_class=average_score_class,
#            ))


        rubrics = Rubric.objects.all()
        rubric_scores = RubricScore.objects.filter(
            content_type=self.content_type,
            object_id=self.object.id,
        )
        for rubric in rubrics:
            scores = rubric_scores.filter(rubric=rubric)
            user_score = scores.filter(user=self.request.user)

            if not user_score.exists():
                user_score = None
            else:
                user_score = user_score.values_list("score__value",
                                                    flat=True)[0]
            average_score =scores.aggregate(
                Avg("score__value")
            )["score__value__avg"]

            if average_score is None:
                average_score_class = None
            else:
                average_score_class = int(average_score)

            data["scores"].append(dict(
                name=rubric.name,
                user_score=user_score,
                user_score_class=user_score,
                average_score=average_score,
                average_score_class=average_score_class,
            ))

        data["finalized"] = data["finalized"] and not rubric_scores.filter(user=self.request.user, confirmed=False).exists()

        not_scored_section = None
        not_scored_tags = set(tags.values_list("id", flat=True)) - \
                          set(user_alignment_scores.values_list("alignment_tag__id",
                                                                flat=True))
        user_rubric_scores = rubric_scores.filter(user=self.request.user)
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

        StandardAlignmentScore.objects.filter(
            content_type=self.content_type,
            object_id=self.object.id,
            user=request.user,
        ).update(confirmed=True)

        RubricScore.objects.filter(
            content_type=self.content_type,
            object_id=self.object.id,
            user=request.user,
        ).update(confirmed=True)

        if isinstance(self.object, Indexed):
            self.object.reindex()

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
