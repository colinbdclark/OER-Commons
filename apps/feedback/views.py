from django import forms
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template, redirect_to
from feedback.models import FEEDBACK_TYPES, FeedbackMessage


class FeedbackForm(forms.ModelForm):

    name = forms.CharField(label=u"Your name:",
                           widget=forms.TextInput(attrs={"class": "text"}))

    email = forms.EmailField(label=u"Your email:",
                           widget=forms.TextInput(attrs={"class": "text"}))

    type = forms.ChoiceField(choices=FEEDBACK_TYPES,
                             label=u"Feedback Type:",
                             widget=forms.Select())

    subject = forms.CharField(label=u"Subject:",
                              widget=forms.TextInput(attrs={"class": "text"}))

    text = forms.CharField(label=u"Text:",
                           widget=forms.Textarea(attrs={"class": "text"}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(FeedbackForm, self).__init__(*args, **kwargs)
        if self.user:
            del self.fields["name"]
            del self.fields["email"]

    class Meta:
        model = FeedbackMessage
        fields = ["name", "email", "type", "subject", "text"]


def feedback(request):

    page_title = u"Feedback"
    breadcrumbs = [{"url": reverse("feedback"), "title": page_title}]

    user = None
    if request.user.is_authenticated():
        user = request.user

    form = FeedbackForm(user=user)

    if request.method == "POST":
        if "send" in request.POST:
            form = FeedbackForm(request.POST, user=user)
            if form.is_valid():
                message = form.save(commit=False)
                if user is not None:
                    message.name = ("%s %s" % (user.first_name, user.last_name)).strip()
                    message.email = user.email
                message.save()
                messages.success(request, u"Thank you, your feedback message was sent to site administrators.")
                return redirect_to(request, reverse("frontpage"), permanent=False)
            else:
                messages.error(request, u"Please correct the indicated errors.")
        elif "cancel" in request.POST:
            return redirect_to(request, reverse("frontpage"), permanent=False)


    return direct_to_template(request, "feedback/feedback.html", locals())
