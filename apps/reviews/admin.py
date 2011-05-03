from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site
from reviews.models import Review
from django.core.urlresolvers import reverse


class ReviewAdmin(ModelAdmin):

    def resource_link(self):
        content_type = self.content_type
        obj = content_type.model_class().objects.get(id=self.object_id)
        admin_url = reverse("admin:%s_%s_change" % (content_type.app_label,
                                                    content_type.model),
                            args=(self.object_id,))
        return """<a href="%s" target="_blank">on site</a> | <a href="%s" target="_blank">in admin</a>""" % (
                                     obj.get_absolute_url(), admin_url)
    resource_link.allow_tags = True
    resource_link.short_description = u"View resource"
        
    list_display = ["__unicode__", resource_link, "timestamp",]
    readonly_fields = ["user", "content_type", "object_id"]

    def has_add_permission(self, request):
        return False


site.register(Review, ReviewAdmin)
