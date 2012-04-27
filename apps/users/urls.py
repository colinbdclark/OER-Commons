from django.conf.urls.defaults import patterns, url
from users.views.login import Login

from users.views.profile import DeleteAccount


urlpatterns = patterns('users.views',
    url(r"^login/?$", Login.as_view(), name="login"),
    url(r"^login-popup/?$", Login.as_view(popup=True), name="login_popup"),
    url(r"^login/form$", "login.render_login_form", name="login_form"),
    url(r"^logout/?$", "login.logout", name="logout"),
    url(r"^registration/?$", "registration.registration", name="registration"),
    url(r"^registration/confirm/?$", "registration.confirm", name="registration_confirm"),
    url(r"^registration/resend/?$", "registration.resend", name="registration_resend"),
    url(r"^welcome/?$", "registration.welcome", name="welcome"),
    url(r"^reset-password/?$", "reset_password.init", name="reset_password_init"),
    url(r"^reset-password/(?P<key>[^/]+)/?$", "reset_password.reset_password", name="reset_password"),
    url(r"^profile/?$", "profile.profile_view", name="profile"),
    url(r"^profile/(?P<user_id>\d+)/?$", "profile.profile_view", name="profile_public"),
    url(r"^profile/edit/?$", "profile.profile_edit", name="profile_edit"),
    url(r"^profile/avatar/update/?$", "profile.avatar_update", name="profile_avatar_update"),
    url(r"^profile/avatar/delete/?$", "profile.avatar_delete", name="profile_avatar_delete"),
    url(r"^profile/geography/?$", "profile.geography", name="profile_geography"),
    url(r"^profile/roles/?$", "profile.roles", name="profile_roles"),
    url(r"^profile/about/?$", "profile.about", name="profile_about"),
    url(r"^profile/delete/?$", DeleteAccount.as_view(), name="profile_delete"),
    url(r"^profile/preferences/?$", "profile.preferences", name="profile_preferences"),
)

