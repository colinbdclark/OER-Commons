from annoying.decorators import ajax_request
from django.contrib.admin.options import ModelAdmin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.functional import update_wrapper
from materials.models.material import PUBLISHED_STATE, DEACCESSIONED_STATE


#noinspection PyUnusedLocal
def publish(modeladmin, request, queryset):
    for obj in queryset:
        obj.workflow_state = PUBLISHED_STATE
        obj.save()
publish.short_description = u"Publish selected items"


#noinspection PyUnusedLocal
def deaccession(modeladmin, request, queryset):
    for obj in queryset:
        obj.workflow_state = DEACCESSIONED_STATE
        obj.save()
deaccession.short_description = u"Deaccession selected items"


class MaterialAdmin(ModelAdmin):

    def url(self):
        url = self.url
        short_url = len(url) < 30 and url or "%s..." % url[:27]
        return """<a target="_blank" title="%(url)s" href="%(url)s">%(short_url)s</a>""" % dict(
            url=url,
            short_url=short_url,
        )
    url.allow_tags = True

    list_display = ["title", url, "http_status", "workflow_state", "creator"]
    list_filter = ["workflow_state", "featured", "http_status", "created_on"]
    search_fields = ["title"]

    actions = [publish, deaccession]

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^(.+)/delete_tag/$',
                wrap(self.delete_tag),
                name='%s_%s_delete_tag' % info),
            url(r'^(.+)/delete_align_tag/$',
                wrap(self.delete_align_tag),
                name='%s_%s_delete_align_tag' % info),

        ) + super(MaterialAdmin, self).get_urls()

        return urlpatterns

    @ajax_request
    def delete_tag(self, request, object_id):

        if not request.is_ajax():
            raise Http404()

        obj = get_object_or_404(self.model, id=int(object_id))

        tag_name = request.POST.get("name")
        if not tag_name:
            return dict(status="error",
                        message=u"Tag name is missing.")

        tags = obj.tags.filter(name=request.POST["name"])
        if not tags.exists():
            return dict(status="error",
                        message=u"Tag with specified name does not exist.")

        tags.delete()

        obj.reindex()

        return dict(status="success")

    @ajax_request
    def delete_align_tag(self, request, object_id):

        if not request.is_ajax():
            raise Http404()

        obj = get_object_or_404(self.model, id=int(object_id))

        tag_id = request.POST.get("id")
        if not tag_id:
            return dict(status="error",
                        message=u"Tag ID is missing.")

        tag_id = int(tag_id)

        tags = obj.alignment_tags.filter(tag=tag_id)
        if not tags.exists():
            return dict(status="error",
                        message=u"Tag with specified ID does not exist.")

        tags.delete()

        obj.reindex()

        return dict(status="success")
