from annoying.decorators import JsonResponse
from common.models import StudentLevel, GeneralSubject, Language
from django import forms
from django.utils.datastructures import MergeDict, MultiValueDict
from django.utils.decorators import method_decorator
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView
from lessons.models import Lesson
from lessons.views import LessonViewMixin
from utils.decorators import login_required
from utils.views import OERViewMixin
import string


class GoalsWidget(forms.widgets.Input):

    input_type = "text"
    EXTRA_INPUTS = 3

    def render(self, name, value, attrs=None):
        if value is None: value = []
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        id_ = final_attrs.get('id', None)
        inputs = []
        for i, v in enumerate(value + ([u""] * self.EXTRA_INPUTS)):
            input_attrs = dict(value=force_unicode(v), **final_attrs)
            if id_:
                # An ID attribute was given. Add a numeric index as a suffix
                # so that the inputs don't all have the same ID attribute.
                input_attrs['id'] = '%s_%s' % (id_, i)
            inputs.append(u'<li><input%s /></li>' % forms.util.flatatt(input_attrs))
        return mark_safe(u'<ul>%s</ul> <a href="#" class="dashed">Add another</a>' % u'\n'.join(inputs))

    def value_from_datadict(self, data, files, name):
        if isinstance(data, (MultiValueDict, MergeDict)):
            value = data.getlist(name)
        else:
            value = data.get(name, None)
        if value is None:
            return value
        return filter(bool, map(string.strip, value))


class DefineForm(forms.ModelForm):

    title = forms.CharField(label=u"Name your OER")

    student_levels = forms.ModelMultipleChoiceField(StudentLevel.objects.all(),
                        label=u"Level:",
                        widget=forms.CheckboxSelectMultiple())

    language = forms.ModelChoiceField(Language.objects.all(),
                        label=u"Language:",
                        widget=forms.Select())

    subjects = forms.ModelMultipleChoiceField(GeneralSubject.objects.all(),
                        label=u"Primary Subject",
                        widget=forms.CheckboxSelectMultiple())

    summary = forms.CharField(widget=forms.Textarea(),
                        label=u"Summary",
                        help_text=u"Quick description of your lesson")

    goals = forms.Field(widget=GoalsWidget(),
                        label=u"Lesson Goals",
                        help_text=u"What do you hope students will learn?")

    class Meta:
        fields = ["title", "student_levels", "language",
                  "subjects", "summary", "goals"]
        model = Lesson


class Define(LessonViewMixin, OERViewMixin, TemplateView):

    template_name = "lessons/authoring/define.html"
    restrict_to_owner = True

    page_title = u"Define Lesson"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(Define, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if getattr(self, "form", None) is None:
            self.form = DefineForm(instance=self.lesson)
        return super(Define, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.form = DefineForm(request.POST, instance=self.lesson)
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
        data = super(Define, self).get_context_data(*args, **kwargs)
        data["form"] = self.form
        data["step_number"] = 1
        return data
