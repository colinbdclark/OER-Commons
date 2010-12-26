from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site
from slider.models import Slide


class SlideAdmin(ModelAdmin):

    list_display = ["title", "order"]
    list_editable = ["order"]


site.register(Slide, SlideAdmin)
