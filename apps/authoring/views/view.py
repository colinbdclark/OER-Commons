from authoring.models import AuthoredMaterial
from django.shortcuts import get_object_or_404
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
        return document.html()

    def get_context_data(self, **kwargs):
        data = super(ViewAuthoredMaterial, self).get_context_data(**kwargs)
        data["material"] = material = get_object_or_404(
            AuthoredMaterial,
            id=int(kwargs["material_id"]),
            published=True,
        )
        data["text"] = ViewAuthoredMaterial.prepare_content(material.text)
        return data
