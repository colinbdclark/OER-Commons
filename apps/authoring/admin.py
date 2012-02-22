from authoring.models import AuthoredMaterial
from django.contrib import admin
from django.core.urlresolvers import reverse


class AuthoredMaterialAdmin(admin.ModelAdmin):

    def title(self):
        if not self.title and self.draft:
            title = self.draft.title
        else:
            title = self.title
        return title or "(No title)"

    def editor(self):
        #noinspection PyUnresolvedReferences
        return """<a href="%s">Open in editor</a>""" % reverse("authoring:write", kwargs=dict(pk=self.pk))
    editor.allow_tags = True

    def author(self):
        return self.author.get_full_name() or self.author.email or unicode(self.author)

    list_display = [title, editor, author, "published"]


admin.site.register(AuthoredMaterial, AuthoredMaterialAdmin)
