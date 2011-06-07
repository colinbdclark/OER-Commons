from django import forms
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from newsletter.tasks import subscribe as do_subscribe


class SubscribeForm(forms.Form):
    
    email = forms.EmailField(label=u"Your email:",
                             widget=forms.TextInput(attrs={"class": "text"}))


def subscribe(request):
    
    if request.method != "POST":
        raise Http404()
    
    api_key = getattr(settings, "MAILCHIMP_API_KEY", None)
    list_id = getattr(settings, "MAILCHIMP_LIST_ID", None)
    
    if not api_key or not list_id:
        raise Http404()
    
    user = request.user
    form = SubscribeForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data["email"]
        kwargs = {}
        if user.is_authenticated():
            kwargs["first_name"] = user.first_name
            kwargs["last_name"] = user.last_name
        do_subscribe.delay(email, **kwargs)
        messages.success(request, u"You are subscribed to OER Commons newsletter now.")

    return redirect("frontpage")
    