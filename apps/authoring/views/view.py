from authoring.views import MaterialViewMixin
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.utils.html import urlize
from django.utils.safestring import mark_safe
from django.views.generic.base import TemplateView
from django.views.generic.detail import BaseDetailView
from materials.models.material import PUBLISHED_STATE
from pyquery import PyQuery as pq


class ViewFullAuthoredMaterial(MaterialViewMixin, BaseDetailView, TemplateView):

    template_name = "authoring/view-full.html"
    preview = False

    def get(self, request, **kwargs):
        object = self.get_object()
        if self.preview:
            if not (request.user == object.material.author or request.user.is_staff):
                raise Http404()
        elif object.slug != self.kwargs["slug"]:
            return redirect(object, permanent=True)
        return super(ViewFullAuthoredMaterial, self).get(request, **kwargs)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        object = get_object_or_404(queryset, pk=self.kwargs["pk"])
        if self.preview:
            return object.get_draft()
        return object

    def get_queryset(self):
        qs = super(ViewFullAuthoredMaterial, self).get_queryset()
        if not self.preview:
            qs = qs.filter(workflow_state=PUBLISHED_STATE)
        return qs

    @classmethod
    def prepare_content(cls, text):
        document = pq(text)
        for embed in document.find("figure.embed"):
            embed = pq(embed)
            #noinspection PyCallingNonCallable
            url = embed.attr("data-url")
            embed.removeAttr("data-url")
            caption = embed.find("figcaption").outerHtml()
            if embed.hasClass("video"):
                content = u"""
                    <script type="text/javascript" src="http://s3.www.universalsubtitles.org/embed.js">
                      ({
                           video_url: "%s",
                           video_config: {
                               width: 500
                           }
                      })
                    </script>
                """ % url
                embed.html(content + caption)

        # Build references
        footnotes = pq("""<div id="footnotes"></div>""")
        for ref in document.find("a.reference"):
            ref = pq(ref)
            text = ref.attr("data-text")
            footnote = pq("""<div class="footnote"><a class="ref" href="%s" id="%s">%s</a> <div>%s</div><div>""" % (
                "#" + ref.attr("id") if ref.attr("id") else "",
                ref.attr("href")[1:],
                ref.text(),
                urlize(text),
            ))
            footnotes.append(footnote)

        # Build table of contents
        prevLevel = 0
        outline = pq("<ul></ul>")

        for i, h in enumerate(document.find("h2,h3")):
            h = pq(h)
            id = "h%i" % (i + 1)
            #noinspection PyCallingNonCallable
            h.attr("id", id)
            if h.is_("h2"):
                level = 0
            else:
                level = 1

            if level > prevLevel:
                for j in xrange(level - prevLevel):
                    outline = pq("<ul></ul>").appendTo(outline)
            elif level < prevLevel:
                for j in xrange(prevLevel - level):
                  outline = outline.parent()

            #noinspection PyCallingNonCallable
            outline.append(
                pq("<li></li>").append(
                    pq("<a></a>").attr("href", "#%s" % id).text(h.text())
                )
            )

            prevLevel = level

        for i in xrange(prevLevel):
            outline = outline.parent()

        return tuple(mark_safe(el.outerHtml()) for el in (document, footnotes, outline))

    def get_context_data(self, **kwargs):
        data = super(ViewFullAuthoredMaterial, self).get_context_data(**kwargs)
        data["text"], data["footnotes"], data["outline"] = ViewFullAuthoredMaterial.prepare_content(self.object.text)
        data["preview"] = self.preview
        data["material"] = self.object.material if self.preview else self.object
        return data

