from django import forms
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
import mailchimp


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
        try:
            list = mailchimp.utils.get_connection().get_list_by_id(list_id)
            user_data = {"EMAIL": email}
            if user.is_authenticated():
                if user.first_name:
                    user_data["FNAME"] = user.first_name
                if user.last_name:
                    user_data["LNAME"] = user.last_name
            list.subscribe(email, user_data)
            messages.success(request, u"A confirmation email has been sent to you. Check your inbox.")
        except:
            messages.success(request, u"Oops! Something went wrong. Please try again later.")
            
    return redirect("frontpage")
    