from authoring.models import AuthoredMaterial
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django.views.generic.base import TemplateView
from pyquery import PyQuery as pq


class ViewAuthoredMaterial(TemplateView):

    template_name = "authoring/view.html"

    @classmethod
    def prepare_content(cls, text):
        document = pq(text)
        for embed in document.find("figure.embed"):
            embed = pq(embed)
            url = embed.attr("data-url")
            embed.removeAttr("data-url")
            caption = embed.find("figcaption").outerHtml()
            if embed.hasClass("video"):
                content = """
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

        # Build table of contents
        prevLevel = 0
        outline = pq("<ul></ul>")

        for i, h in enumerate(document.find("h2,h3")):
            h = pq(h)
            id = "h%i" % (i + 1)
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

            outline.append(
                pq("<li></li>").append(
                    pq("<a></a>").attr("href", "#%s" % id).text(h.text())
                )
            )

            prevLevel = level

        for i in xrange(prevLevel):
            outline = outline.parent()

        return mark_safe(document.outerHtml()), mark_safe(outline.outerHtml())

    def get_context_data(self, **kwargs):
        data = super(ViewAuthoredMaterial, self).get_context_data(**kwargs)
        data["material"] = material = get_object_or_404(
            AuthoredMaterial,
            id=int(kwargs["material_id"]),
            published=True,
        )
        data["text"], data["outline"] = ViewAuthoredMaterial.prepare_content(material.text)
        return data
