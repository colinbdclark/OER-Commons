from django import forms
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.urlresolvers import resolve, reverse
from django.http import Http404, HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from utils.decorators import login_required
from django.template.loader import render_to_string
from django.core.mail.message import EmailMessage
from annoying.decorators import JsonResponse


class SendThisForm(forms.Form):

    path = forms.CharField(widget=forms.HiddenInput())

    email = forms.EmailField(label=u"Send to",
                             help_text=u"The e-mail address to send this link to.",
                             widget=forms.TextInput(attrs={"class": "text"}))

    comment = forms.CharField(label=u"Comment",
                             help_text=u"A comment about this link.",
                             widget=forms.Textarea(attrs={"class": "text"}),
                             required=False)

    def clean_path(self):
        path = self.cleaned_data["path"]
        try:
            view, args, kwargs = resolve(path)
            view(self.request, *args, **kwargs)
        except:
            raise forms.ValidationError(u"Invalid path")
        return path

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.user = kwargs.pop("user", None)
        only_path = kwargs.pop("only_path", False)
        super(SendThisForm, self).__init__(*args, **kwargs)
        if only_path:
            self.fields["email"].required = False

    def send(self):
        if not self.user:
            return
        site_url = "http://%s" % Site.objects.get_current().domain
        link = site_url + self.cleaned_data["path"]
        comment = self.cleaned_data["comment"]
        body = render_to_string("sendthis/send-this-email.html",
                                dict(site_url=site_url,
                                     link=link,
                                     comment=comment,
                                     user=self.user))
        message = EmailMessage(u"Invite you to OER Commons site", body,
                               self.user.email, [self.cleaned_data["email"]])
        message.content_subtype = "html"
        message.send()


@login_required
def send(request):

    form = SendThisForm(request.REQUEST, request=request, only_path=True)
    form.is_valid()
    if not hasattr(form, "cleaned_data"):
        raise Http404()
    path = form.cleaned_data["path"]

    link = "http://%s%s" % (Site.objects.get_current().domain, path)
    page_title = u"Send This"
    breadcrumbs = [{"url": reverse("send-this"), "title": page_title}]

    if "cancel" in request.REQUEST:
        return HttpResponseRedirect(path)
    if "send" in request.REQUEST:
        form = SendThisForm(request.REQUEST, request=request, user=request.user)
        if form.is_valid():
            form.send()
            message = u"Email was sent to %s" % form.cleaned_data["email"]
            if request.is_ajax():
                return JsonResponse(dict(message=message))
            messages.success(request, message)
            return HttpResponseRedirect(path)
        else:
            messages.error(request, u"Please correct the indicated errors.")
    else:
        form = SendThisForm()

    return direct_to_template(request, "sendthis/send-this.html", locals())
