from annoying.decorators import JsonResponse, ajax_request
from annoying.functions import get_object_or_None
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import linebreaksbr
from django.utils.decorators import method_decorator
from django.views.generic import View
from reviews.models import Review
from utils.decorators import login_required


class ReviewForm(forms.ModelForm):

    def clean_text(self):
        return self.cleaned_data["text"].strip()

    class Meta:
        model = Review
        fields = ["text"]


class ReviewView(View):

    #noinspection PyUnusedLocal
    @method_decorator(login_required)
    @method_decorator(ajax_request)
    def post(self, request, *args, **kwargs):
        content_type = get_object_or_404(ContentType, id=int(kwargs["content_type_id"]))
        object_id = int(kwargs["object_id"])
        get_object_or_404(content_type.model_class(), id=object_id)

        review = get_object_or_None(
            Review,
            user=request.user,
            content_type=content_type,
            object_id=object_id,
        )

        if "delete" in request.POST:
            if not review:
                return HttpResponseBadRequest(u"Review does not exist.")
            else:
                review.delete()
                return JsonResponse(dict(
                    status="success",
                    message=u"Your comment was deleted.",
                ))

        if not review:
            review = Review(
                content_type=content_type,
                object_id=object_id,
                user=request.user,
            )
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save()
            return JsonResponse(dict(
                status="success",
                message=u"Your comment was saved.",
                text=linebreaksbr(review.text),
                author=review.user.get_profile().name,
            ))

        errors = {}
        #noinspection PyUnresolvedReferences
        for field, errors_list in form.errors.items():
            errors[field] = errors_list[0]
        return JsonResponse(dict(status="error",
                                 errors=errors))
