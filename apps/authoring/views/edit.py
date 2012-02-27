from authoring.views import EditMaterialViewMixin
from authoring.views.describe import DescribeForm
from authoring.views.submit import SubmitForm
from authoring.views.write import WriteForm
from django.views.generic import TemplateView


class Edit(EditMaterialViewMixin, TemplateView):

    template_name = "authoring/edit.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(Edit, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(Edit, self).get_context_data(**kwargs)
        data["write_form"] = WriteForm(instance=self.object)
        data["describe_form"] = DescribeForm(instance=self.object)
        data["submit_form"] = SubmitForm(instance=self.object)
        data["hide_global_tabs"] = True
        return data
