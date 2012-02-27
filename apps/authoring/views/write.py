from authoring.models import AuthoredMaterialDraft
from authoring.views import EditMaterialProcessForm
from django import forms


class WriteForm(forms.ModelForm):

    # TODO: clean up HTML from `text` field.
    # using lxml clean. Remove all styles, Keep only allowed classes,
    # remove scripts, styles, forms, iframes, objects, embeds

    class Meta:
        model = AuthoredMaterialDraft
        fields = ["text"]
        widgets = dict(
            text=forms.HiddenInput(),
        )


class Write(EditMaterialProcessForm):

    form_class = WriteForm
