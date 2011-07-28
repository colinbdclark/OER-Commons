from annoying.decorators import ajax_request
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.mail.message import EmailMessage
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.generic.simple import direct_to_template
from django.shortcuts import redirect
from geo.models import CountryIPDiapason
from sorl.thumbnail.shortcuts import delete
from users.models import Profile
from users.views.forms import UserInfoForm, ChangePasswordForm, GeographyForm,\
    RolesForm, AboutMeForm, AvatarForm
from utils.decorators import login_required
from utils.shortcuts import ajax_form_success, ajax_form_error
import json
import time


@login_required
def profile_view(request):

    page_title = u"My Profile"
    breadcrumbs = [{"url": reverse("users:profile"), "title": page_title}]
    hide_global_notifications = True

    user = request.user
    profile = Profile.objects.get_or_create(user=user)[0]

    return direct_to_template(request, "users/profile.html", locals())


@login_required
def profile_edit(request):

    user = request.user
    profile = Profile.objects.get_or_create(user=user)[0]

    # If a user has all main fields filled we redirect him
    # to the next not-filled subform
    if "unfilled" in request.GET:
        if user.first_name and user.last_name and user.email:
            if not all([profile.country, profile.connect_with]):
                return redirect("users:profile_geography")
            if profile.country and profile.country.code == "US" and not profile.us_state:
                return redirect("users:profile_geography")
            if not profile.roles.exists():
                return redirect("users:profile_roles")
            if profile.roles.filter(is_educator=True).exists() and (not profile\
            .educator_student_levels.exists() or not profile.educator_subjects\
            .exists()):
                return redirect("users:profile_roles")
            if not all([profile.about_me, profile.website_url,
                        profile.facebook_id, profile.twitter_id,
                        profile.skype_id]):
                return redirect("users:profile_about")

    page_title = u"My Profile"
    breadcrumbs = [{"url": reverse("users:profile"), "title": page_title}]
    hide_global_notifications = True

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
                                       body, to=[user.email])
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

    return direct_to_template(request, "users/profile-edit.html", locals())


@login_required
def avatar_update(request):
    response = dict(status="error", message=u"")

    form = AvatarForm(request.POST, request.FILES)

    if form.is_valid():
        user = request.user
        profile = Profile.objects.get_or_create(user=user)[0]
        if profile.avatar:
            delete(profile.avatar)
        avatar = form.cleaned_data["file"]
        if avatar.content_type == "image/jpeg":
            extension = ".jpg"
        elif avatar.content_type == "image/png":
            extension = ".png"
        elif avatar.content_type == "image/gif":
            extension = ".gif"
        else:
            extension = ""
        filename = "%i%s" % (user.id, extension)
        profile.avatar.save(filename, avatar, save=False)
        profile.hide_avatar = False
        profile.save()

        response["status"] = "success"
        response["message"] = u"Your picture is saved."
        response["url"] = profile.get_avatar_url() + "?" + str(int(time.time()))

    else:
        response["message"] = form.errors["file"][0]
        return response

    # We don't use application/json content type here because IE misinterprets it.
    return HttpResponse(json.dumps(response))



@login_required
@ajax_request
def avatar_delete(request):
    response = dict(status="error", message=u"")

    user = request.user
    profile = Profile.objects.get_or_create(user=user)[0]
    if profile.avatar:
        delete(profile.avatar)
    profile.hide_avatar = True
    profile.save()

    response["status"] = "success"
    response["message"] = u"Your picture is deleted."
    response["url"] = profile.get_avatar_url()
    return response


@login_required
def geography(request):

    page_title = u"My Profile"
    breadcrumbs = [{"url": reverse("users:profile"), "title": page_title}]
    hide_global_notifications = True

    user = request.user
    profile = Profile.objects.get_or_create(user=user)[0]

    country = profile.country
    if not country:
        ip = request.META.get("REMOTE_ADDR", None)
        if ip:
            country = CountryIPDiapason.objects.get_country_by_ip(ip)
            
    initial = {"country": country, "us_state": profile.us_state}

    is_US = country and country.code == "US"

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
    hide_global_notifications = True

    user = request.user
    profile = Profile.objects.get_or_create(user=user)[0]

    form = RolesForm(instance=profile)
    is_educator = profile.roles.filter(is_educator=True).exists()

    if request.method == "POST":
        form = RolesForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            if request.is_ajax():
                return ajax_form_success(form.success_message)
            
            return redirect("users:profile_about")
        
        else:
            if request.is_ajax():
                return ajax_form_error(form, form.error_message)
            
            messages.error(request, form.error_message)

    return direct_to_template(request, "users/profile-roles.html", locals())


@login_required
def about(request):

    page_title = u"My Profile"
    breadcrumbs = [{"url": reverse("users:profile"), "title": page_title}]
    hide_global_notifications = True

    user = request.user
    profile = Profile.objects.get_or_create(user=user)[0]

    form = AboutMeForm(instance=profile)

    if request.method == "POST":
        form = AboutMeForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            if request.is_ajax():
                return ajax_form_success(form.success_message)
            
            return redirect("frontpage")
        
        else:
            if request.is_ajax():
                return ajax_form_error(form, form.error_message)
            
            messages.error(request, form.error_message)

    return direct_to_template(request, "users/profile-about.html", locals())
