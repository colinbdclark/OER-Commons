from authoring.models import AuthoredMaterial
from django.contrib import admin
from django.core.urlresolvers import reverse


class AuthoredMaterialAdmin(admin.ModelAdmin):

    def editor(self):
        #noinspection PyUnresolvedReferences
        return """<a href="%s">Open in editor</a>""" % reverse("authoring:write", kwargs=dict(pk=self.pk))
    editor.allow_tags = True

    list_display = ["title", editor, "author", "published"]


admin.site.register(AuthoredMaterial, AuthoredMaterialAdmin)
