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
        document = pq("<div></div>").html(text)
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
            for a in footnote.find("div a"):
                pq(a).attr("target", "_blank")
            footnotes.append(footnote)

        # Build table of contents
        toc = pq("<div></div>")

        for i, h in enumerate(document.find("h2,h3")):
            h = pq(h)
            id = "h%i" % (i + 1)
            #noinspection PyCallingNonCallable
            h.attr("id", id)
            if h.is_("h2"):
                class_ = "level-0"
            else:
                class_ = "level-1"
            header = pq("<div></div>").addClass("header").addClass(class_)
            #noinspection PyCallingNonCallable
            header.append(pq("<a></a>").attr("href", "#%s" % id).text(h.text()))
            toc.append(header)

        return tuple(mark_safe(el) for el in (document.html(), footnotes.outerHtml(), toc.html()))

    def get_context_data(self, **kwargs):
        data = super(ViewFullAuthoredMaterial, self).get_context_data(**kwargs)
        data["text"], data["footnotes"], data["toc"] = ViewFullAuthoredMaterial.prepare_content(self.object.text)
        data["preview"] = self.preview
        data["material"] = self.object.material if self.preview else self.object
        return data

