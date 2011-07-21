from annoying.decorators import JsonResponse
from django import forms
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from lessons.models import Lesson, Group
from lessons.views import LessonViewMixin
from utils.decorators import login_required
from utils.views import OERViewMixin

import datetime


class OrganizeLessonForm(forms.ModelForm):

    group = forms.ModelChoiceField(Group.objects.all(),
                label=u"Add to an item group",
                help_text=u"and keep your items straight")

    instruction_date = forms.DateField(initial=,
                label=u"What is the indented date of instruction?",
                help_text=u"we'll put it in your calendar in 'My Items'")



    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super(OrganizeLessonForm, self).__init__(*args, **kwargs)
        self.fields["group"].queryset = self.fields["group"].queryset.filter(user=user)

    class Meta:
        model = Lesson
        fields = ["group", "keywords", "instruction_date"]


class OrganizeLesson(LessonViewMixin, OERViewMixin, TemplateView):

    template_name = "lessons/authoring/lesson-organize.html"
    restrict_to_owner = True

    def get_page_title(self):
        if self.lesson.title:
            return u'Edit "%s"' % self.lesson.title
        return u"Edit Lesson"

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(Organize, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if getattr(self, "form", None) is None:
            self.form = OrganizeLessonForm(instance=self.lesson)
        return super(OrganizeLesson, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.form = OrganizeLessonForm(request.POST, instance=self.lesson)
        if self.form.is_valid():
            self.form.save()
            if request.is_ajax():
                return JsonResponse(dict(status="success", message=u"Changes were saved."))
        else:
            if request.is_ajax():
                errors = {}
                for field_name, errors_list in self.form.errors.items():
                    errors[field_name] = errors_list[0]
                return JsonResponse(dict(status="error", errors=errors))

        return self.get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        data = super(OrganizeLesson, self).get_context_data(*args, **kwargs)
        data["form"] = self.form
        return data
