from authoring.views.view import ViewFullAuthoredMaterial
from django.http import HttpResponse
from django.template.loader import render_to_string
from sx.pisa3 import pisaDocument
import StringIO


class AsPdf(ViewFullAuthoredMaterial):

    template_name = "authoring/pdf.html"

    def get(self, request, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)

        html = render_to_string(self.template_name, context)
        if "html" in request.GET:
            return HttpResponse(html)
        result = StringIO.StringIO()
        pdf = pisaDocument(StringIO.StringIO(html.encode("utf-8")), result, show_error_as_pdf=True, encoding="UTF-8")
        response = HttpResponse(result.getvalue(), mimetype='application/pdf')
#        response["Content-Disposition"] = "attachment; filename=%s.pdf" % self.object.title.encode("utf-8")
        return response
