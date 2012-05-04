from authoring.views.view import ViewFullAuthoredMaterial
from django.conf import settings
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from sx.pisa3 import pisaDocument
import os
import StringIO


FONTS = {
    "Times_New_Roman.ttf": "font-family: Times New Roman;",
    "Times_New_Roman_Bold.ttf": "font-family: Times New Roman; font-weight: bold;",
    "Times_New_Roman_Italic.ttf": "font-family: Times New Roman; font-style: italic;",
    "Times_New_Roman_Bold_Italic.ttf": "font-family: Times New Roman; font-weight: bold; font-style: italic;",
    "Arial.ttf": "font-family: Arial;",
    "Arial_Bold.ttf": "font-family: Arial; font-weight: bold;",
    "Arial_Italic.ttf": "font-family: Arial; font-style: italic;",
    "Arial_Bold_Italic.ttf": "font-family: Arial; font-weight: bold; font-style: italic;",
}


class AsPdf(ViewFullAuthoredMaterial):

    template_name = "authoring/pdf.html"

    def get_context_data(self, **kwargs):
        data = super(AsPdf, self).get_context_data(**kwargs)
        fonts_dir = getattr(settings, "FONTS_DIR", None)
        fonts = []
        if fonts_dir and os.path.exists(fonts_dir) and os.path.isdir(fonts_dir):
            available_fonts = set(os.listdir(fonts_dir))
            for filename, spec in sorted(FONTS.items()):
                if filename in available_fonts:
                    fonts.append("@font-face: {%s src: url(%s); }" % (spec, os.path.join(fonts_dir, filename)))
        data["fonts"] = "\n\n".join(fonts)
        data["STATIC_ROOT"] = settings.STATIC_ROOT
        return data

    def get(self, request, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)

        html = render_to_string(self.template_name, RequestContext(request, context))

        html = html.replace("""src="%s""" % settings.STATIC_URL, """src="%s/""" % settings.STATIC_ROOT)

        if "html" in request.GET:
            return HttpResponse(html)
        result = StringIO.StringIO()
        pdf = pisaDocument(StringIO.StringIO(html.encode("utf-8")), result, show_error_as_pdf=True, encoding="UTF-8")
        response = HttpResponse(result.getvalue(), mimetype='application/pdf')
        response["Content-Disposition"] = "filename=%s.pdf" % self.object.title.encode("utf-8")
        return response
