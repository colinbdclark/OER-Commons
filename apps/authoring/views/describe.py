from itertools import chain
from authoring.models import AuthoredMaterialDraft
from authoring.views import EditMaterialViewMixin
from core.forms import MultipleAutoCreateField
from django import forms
from django.contrib import messages
from django.forms import ModelMultipleChoiceField
from django.forms.widgets import CheckboxInput
from django.shortcuts import  redirect
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.views.generic import UpdateView
from materials.models import GeneralSubject, Language


class SubjectsWidget(forms.CheckboxSelectMultiple):

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            if i == (len(self.choices) / 2):
                output.append(u'</ul>')
                output.append(u'<ul>')

            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<li><label%s>%s %s</label></li>' % (label_for, rendered_cb, option_label))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))


class DescribeForm(forms.ModelForm):

    learning_goals = MultipleAutoCreateField("title")
    keywords = MultipleAutoCreateField("name", required=False)
    subjects = ModelMultipleChoiceField(GeneralSubject.objects.all(), widget=SubjectsWidget())
    language = forms.ModelChoiceField(queryset=Language.objects.all(), required=False)

    class Meta:
        model = AuthoredMaterialDraft
        fields = ["summary", "learning_goals", "keywords", "subjects", "grade_level", "language"]
        widgets = dict(
            summary=forms.Textarea(attrs=dict(placeholder=u"Please give a short summary of your resource. This will appear as the preview in search results."))
        )

class Describe(EditMaterialViewMixin, UpdateView):

    template_name = "authoring/describe.html"
    form_class = DescribeForm

    def form_invalid(self, form):
        messages.error(self.request, u"Please correct the indicated errors.")
        return super(Describe, self).form_invalid(form)

    def form_valid(self, form):
        form.save()
        if self.request.POST.get("next") == "true":
            return redirect("authoring:submit", pk=self.object.material.pk)
        elif self.request.POST.get("next") == "false":
            return redirect("authoring:write", pk=self.object.material.pk)
        return self.render_to_response(self.get_context_data(form=form))
