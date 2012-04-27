from annoying.decorators import ajax_request
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.mail.message import EmailMessage
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.views.generic.simple import direct_to_template
from django.views.generic import View
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from geo.models import CountryIPDiapason
from sorl.thumbnail.shortcuts import delete
from haystack.query import SearchQuerySet, SQ
from users.models import Profile, PREFERENCE_FIELDS
from users.views.forms import UserInfoForm, ChangePasswordForm, GeographyForm,\
    RolesForm, AboutMeForm, AvatarForm, PreferencesForm, PrivacyForm
from utils.decorators import login_required
from utils.shortcuts import ajax_form_success, ajax_form_error
from authoring.models import AuthoredMaterial
from materials.models.material import PUBLISHED_STATE
from materials.models import CommunityItem, Course, Library
from rubrics.models import Evaluation
from saveditems.models import SavedItem
from myitems.views import MaterialsIndex, django_ct_from_model
import json
import time
from collections import defaultdict
from operator import or_, attrgetter
from itertools import chain
import datetime


SUBMITTED_MODELS = set([
    CommunityItem,
    Course,
    Library,
])

CREATED_MODELS = set([
    AuthoredMaterial,
])

ACTIVITY_ITEMS_COUNT = 6

MINDATETIME = datetime.datetime(datetime.MINYEAR, 1, 1)


def django_ct_from_id(id_):
    ct = ContentType.objects.get_for_id(id_)
    return '.'.join((ct.app_label, ct.model))


def profile_view(request, user_id=None):
    show_activity = True
    if user_id:
        user = get_object_or_404(User, id=int(user_id))
        profile = Profile.objects.get_or_create(user=user)[0]
        if user == request.user:
            public = False
        else:
            public = True
            if profile.privacy == "hide":
                raise Http404()
            elif profile.privacy == "basic":
                show_activity = False
    elif not request.user.is_authenticated():
        raise Http404()
    else:
        public = False
        user = request.user
        profile = Profile.objects.get_or_create(user=user)[0]


    created_count = AuthoredMaterial.objects.filter(
        author=user,
        workflow_state=PUBLISHED_STATE,
    ).count()

    all_saved = defaultdict(list)
    all_saved_queryset = SearchQuerySet().filter(saved_by=user.id).models(*SUBMITTED_MODELS)
    for result in all_saved_queryset:
        all_saved[(result.app_label, result.model_name)].append(result.pk)
    all_saved_count = all_saved_queryset.count()
    all_submitted_count = SearchQuerySet().filter(creator=user.id).models(*SUBMITTED_MODELS).count()

    evaluated_queryset = Evaluation.objects.filter(user=user, confirmed=True)
    evaluated_count = evaluated_queryset.count()
    if all_saved:
        queries = (
            Q(
                content_type=ContentType.objects.get_by_natural_key(*k).id,
                object_id__in=ids
            )
            for k, ids in all_saved.iteritems()
        )
        query = reduce(or_, queries)
        saved_evaluated_count = evaluated_queryset.filter(query).count()
    else:
        saved_evaluated_count = 0

    if show_activity:
        evaluations = Evaluation.objects.filter(
            user=user,
            confirmed=True
        ).order_by("-timestamp").values_list('content_type', 'object_id', 'timestamp')[:ACTIVITY_ITEMS_COUNT]
        saved_items = SavedItem.objects.filter(
            user=user
        ).order_by("-timestamp").values_list('content_type', 'object_id', 'timestamp')[:ACTIVITY_ITEMS_COUNT]

        items_timestamp = defaultdict(dict)
        for content_type, object_id, timestamp in chain(evaluations, saved_items):
            ids = items_timestamp[content_type]
            if object_id not in ids or ids[object_id] < timestamp:
                ids[object_id] = timestamp

        if items_timestamp:
            items_timestamp = dict(
                (django_ct_from_id(content_type), ids)
                for content_type, ids in items_timestamp.iteritems()
            )

            query = reduce(or_,
                (
                    SQ(
                        django_ct=django_ct,
                        django_id__in=list(ids)
                    )
                    for django_ct, ids in items_timestamp.iteritems()
                )
            )
            results = list(SearchQuerySet().filter(query))
            for result in results:
                result.published_on = items_timestamp[result.content_type()][int(result.pk)]
        else:
            results = []

        submitted_query = (
            reduce(or_, (SQ(django_ct=django_ct_from_model(model)) for model in SUBMITTED_MODELS))
            & SQ(creator=user.id)
        )
        created_query = (
            reduce(or_, (SQ(django_ct=django_ct_from_model(model)) for model in CREATED_MODELS))
            & SQ(creator=user.id, is_displayed=True)
        )

        results.extend(SearchQuerySet().filter(submitted_query | created_query).models(
            *SUBMITTED_MODELS|CREATED_MODELS).order_by('-published_on')[:ACTIVITY_ITEMS_COUNT]
        )

        for result in results:
            if not result.published_on:
                result.published_on = MINDATETIME

        results.sort(key=attrgetter('published_on'), reverse=True)
        results = results[:ACTIVITY_ITEMS_COUNT]
        model_to_pks = defaultdict(list)
        for result in results:
            model_to_pks[result.model].append(int(result.pk))

        materials_index = MaterialsIndex(
            results,
            user,
            model_to_pks,
        )
        items = materials_index.items
    else:
        items = []

    return direct_to_template(request, "users/profile.html", {
        'page_title': u"My Profile",
        'profile': profile,
        'public': public,
        'created_count': created_count,
        'evaluated_count': evaluated_count,
        'saved_count': all_saved_count-saved_evaluated_count,
        'submitted_count': all_submitted_count-(evaluated_count-saved_evaluated_count),
        'items': items,
        'index_type': 'pics',
    })


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
            if profile.roles.filter(is_educator=True).exists() and \
               (not profile.educator_student_levels.exists() or not profile.educator_subjects.exists()):
                return redirect("users:profile_roles")
            if not all([profile.about_me, profile.website_url,
                        profile.facebook_id, profile.twitter_id,
                        profile.skype_id]):
                return redirect("users:profile_about")

    page_title = u"My Profile"
    hide_global_notifications = True

    user_info_form = UserInfoForm(instance=user)
    change_password_form = ChangePasswordForm()

    if request.method == "POST":

        if "user-info" in request.POST:
            user_info_form = UserInfoForm(request.POST, instance=user)

            if user_info_form.is_valid():
                user_info_form.save()

                if request.is_ajax():
                    return ajax_form_success(user_info_form.success_message)

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

            return redirect("users:profile")

        else:
            if request.is_ajax():
                return ajax_form_error(form, form.error_message)

            messages.error(request, form.error_message)

    return direct_to_template(request, "users/profile-about.html", locals())


def get_preferences_from_cookies(request):
    preferences = {}
    for field_name, (cookie_name, default_value) in PREFERENCE_FIELDS.items():
        value = default_value
        cookie_value = request.COOKIES.get(cookie_name, None)
        if cookie_value:
            try:
                value = json.loads(cookie_value)
            except ValueError:
                pass
        preferences[field_name] = value

    return preferences


def save_preferences_to_cookies(response, data):
    max_age = 3600 * 24 * 365 * 2 # Two years
    for field_name, value in data.items():
        if field_name not in PREFERENCE_FIELDS:
            continue
        cookie_name = PREFERENCE_FIELDS[field_name][0]
        value = json.dumps(value)
        response.set_cookie(cookie_name, value, max_age=max_age)


def delete_preference_cookies(response):
    for cookie_name, default_value in PREFERENCE_FIELDS.values():
        response.delete_cookie(cookie_name)


@csrf_protect
def preferences(request):

    page_title = u"My Preferences"

    user = request.user if request.user.is_authenticated() else None
    instance = None
    FormClass = PrivacyForm if user else PreferencesForm
    if user:
        try:
            instance = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            pass
    if instance:
        form = FormClass(instance=instance)
    else:
        form = FormClass(initial=get_preferences_from_cookies(request))

    if request.method == "POST":
        if user:
            if not instance:
                instance = Profile(user=user)
            form = FormClass(request.POST, instance=instance)
            if form.is_valid():
                instance = form.save()
                messages.success(request, form.success_message)
                form = FormClass(instance=instance)
                response = direct_to_template(request, "users/preferences.html", locals())
                delete_preference_cookies(response)
                return response
            else:
                messages.error(request, form.error_message)
        else:
            form = FormClass(request.POST)
            if form.is_valid():
                messages.success(request, form.success_message)
                data = form.cleaned_data
                form = FormClass(initial=data)
                response = direct_to_template(request, "users/preferences.html", locals())
                save_preferences_to_cookies(response, data)
                return response
            else:
                messages.error(request, form.error_message)

    return direct_to_template(request, "users/preferences.html", locals())


class DeleteAccount(View):

    @method_decorator(login_required)
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteAccount, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = request.user
        profile = user.get_profile()
        profile.privacy = "hide"
        profile.save()
        user.is_active = False
        user.save()
        logout(request)
        messages.success(self.request,
             u"Your account was removed. To restore it please contact " \
             u"site administration.")
        return redirect("frontpage")
