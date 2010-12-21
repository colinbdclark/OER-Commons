from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site
from feedback.models import FeedbackMessage


class FeedbackMessageAdmin(ModelAdmin):

    list_display = ["subject", "type", "name", "email", "spam", "timestamp"]
    list_filter = ["type", "spam", "timestamp"]
    readonly_fields = ["name", "email", "type", "subject", "text", "timestamp"]


site.register(FeedbackMessage, FeedbackMessageAdmin)
