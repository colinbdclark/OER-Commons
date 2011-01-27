from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site
from reviews.models import Review


class ReviewAdmin(ModelAdmin):

    list_display = ["__unicode__", "timestamp"]
    readonly_fields = ["user", "content_type", "object_id"]

    def has_add_permission(self, request):
        return False


site.register(Review, ReviewAdmin)
