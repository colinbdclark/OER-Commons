from authoring.models import AuthoredMaterial, AuthoredMaterialDraft
from django.contrib import admin
from django.core.urlresolvers import reverse
from materials.models.material import PRIVATE_STATE, PUBLISHED_STATE


class AuthoredMaterialAdmin(admin.ModelAdmin):

    def publish(self, request, queryset):
        for material in queryset:
            try:
                draft = AuthoredMaterialDraft.objects.get(material=material)
            except AuthoredMaterialDraft.DoesNotExist:
                continue
            AuthoredMaterial.publish_draft(draft)
    publish.short_description = "Publish selected materials"

    def unpublish(self, request, queryset):
        for material in queryset.filter(workflow_state=PUBLISHED_STATE):
            material.workflow_state = PRIVATE_STATE
            material.save()
    unpublish.short_description = "Unpublish selected materials"

    actions = [
        publish,
        unpublish,
    ]

    def title(self):
        if not self.title and self.draft:
            title = self.draft.title
        else:
            title = self.title
        return title or "(No title)"

    def editor(self):
        #noinspection PyUnresolvedReferences
        return """<a href="%s" target="_blank">Open in editor</a>""" % reverse("authoring:edit", kwargs=dict(pk=self.pk))
    editor.allow_tags = True

    def view_on_site(self):
        if self.published():
            return """<a href="%s" target="_blank">View on site</a>""" % reverse("authoring:view", kwargs=dict(pk=self.pk))
        return u""
    view_on_site.allow_tags = True


    def author(self):
        return self.author.get_full_name() or self.author.email or unicode(self.author)

    def published(self):
        return self.workflow_state == PUBLISHED_STATE

    list_display = [title, editor, view_on_site, author, published]


admin.site.register(AuthoredMaterial, AuthoredMaterialAdmin)
