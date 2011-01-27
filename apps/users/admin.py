from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site
from users.models import RegistrationConfirmation


def user(obj):
    user = obj.user
    return "%s <%s>" % (user.username, user.email)


class RegistrationConfirmationAdmin(ModelAdmin):

    list_filter = ["confirmed", ]
    list_display = [user, "key", "timestamp", "confirmed", ]
    readonly_fields = ["user", "key", "timestamp", "confirmed"]

    def has_add_permission(self, request):
        return False


site.register(RegistrationConfirmation, RegistrationConfirmationAdmin)
