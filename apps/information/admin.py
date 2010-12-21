from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site
from information.models import HelpTopic, AboutTopic


class TopicAdmin(ModelAdmin):
    list_display = ["title", "order"]
    list_editable = ["order"]


site.register(HelpTopic, TopicAdmin)
site.register(AboutTopic, TopicAdmin)
