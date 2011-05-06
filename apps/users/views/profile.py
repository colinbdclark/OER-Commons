from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.mail.message import EmailMessage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.views.generic.simple import direct_to_template
from users.models import Profile
from users.views.forms import UserInfoForm, ChangePasswordForm, GeographyForm,\
    RolesForm
from utils.decorators import login_required
from utils.shortcuts import ajax_form_success, ajax_form_error
from django.shortcuts import redirect
from geo.models import CountryIPDiapason


@login_required
def profile(request):

    page_title = u"My Profile"
    breadcrumbs = [{"url": reverse("users:profile"), "title": page_title}]

    user = request.user
    profile = Profile.objects.get_or_create(user=user)[0]
    user_info_form = UserInfoForm(instance=user)
    change_password_form = ChangePasswordForm()

    if request.method == "POST":
        
        if "user-info" in request.POST:
            user_info_form = UserInfoForm(request.POST, instance=user)
            
            if user_info_form.is_valid():
                user_info_form.save()
                
                if request.is_ajax():
                    return ajax_form_success(user_info_form.success_mesage)
                
                return redirect("users:profile_geography")
                
            else:
                if request.is_ajax():
                    return ajax_form_error(user_info_form, user_info_form.error_message)
                
                messages.error(request, user_info_form.error_message)
                    
        elif "change-password" in request.POST:
            change_password_form = ChangePasswordForm(request.POST, instance=user)
            
            if change_password_form.is_valid():
                change_password_form.save()
                body = render_to_string("users/emails/change-password.html",
                                        dict(user=user,
                   new_password=change_password_form.cleaned_data["new_password"],
                   domain=Site.objects.get_current().domain))
                message = EmailMessage(u"OER Commons: Password Changed",
                                       body, None, [user.email])
                message.content_subtype = "html"
                message.send()
                
                if request.is_ajax():
                    return ajax_form_success(change_password_form.success_message)
                
                messages.success(request, change_password_form.success_message)
                change_password_form = ChangePasswordForm()
                
            else:
                if request.is_ajax():
                    return ajax_form_error(change_password_form,
                                           change_password_form.error_message)
                    
                messages.error(request, change_password_form.error_message)

    return direct_to_template(request, "users/profile.html", locals())


@login_required
def geography(request):

    page_title = u"My Profile"
    breadcrumbs = [{"url": reverse("users:profile"), "title": page_title}]

    user = request.user
    profile = Profile.objects.get_or_create(user=user)[0]

    initial = None
    if not profile.country:
        ip = request.META.get("REMOTE_ADDR", None)
        if ip:
            country = CountryIPDiapason.objects.get_country_by_ip(ip)
            if country:
                initial = dict(country=country)

    form = GeographyForm(instance=profile, initial=initial)

    if request.method == "POST":
        form = GeographyForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            if request.is_ajax():
                return ajax_form_success(form.success_message)
            
            return redirect("users:profile_roles")
        
        else:
            if request.is_ajax():
                return ajax_form_error(form, form.error_message)
            
            messages.error(request, form.error_message)

    return direct_to_template(request, "users/profile-geography.html", locals())


@login_required
def roles(request):

    page_title = u"My Profile"
    breadcrumbs = [{"url": reverse("users:profile"), "title": page_title}]

    user = request.user
    profile = Profile.objects.get_or_create(user=user)[0]

    form = RolesForm(instance=profile)

    if request.method == "POST":
        form = RolesForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            if request.is_ajax():
                return ajax_form_success(form.success_message)
            
            return redirect("users:profile_roles")
        
        else:
            if request.is_ajax():
                return ajax_form_error(form, form.error_message)
            
            messages.error(request, form.error_message)

    return direct_to_template(request, "users/profile-roles.html", locals())

