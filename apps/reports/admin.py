from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site
from reports.models import Report


def download_link(obj):
    return """<a href="%s">Download</a>""" % obj.file.url
download_link.allow_tags = True


class ReportAdmin(ModelAdmin):


    list_display = ["__unicode__", download_link]
    list_filters = ["type"]

    def has_add_permission(self, request):
        return False

    def has_edit_permission(self, request):
        return False

site.register(Report, ReportAdmin)
