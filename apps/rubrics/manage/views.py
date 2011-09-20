from annoying.decorators import JsonResponse
from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import TemplateView, FormView
from users.views.login import LoginForm


class Login(FormView):

    template_name = "rubrics/manage/login.html"
    form_class = LoginForm

    def get_form_kwargs(self):
        kwargs = super(Login, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        login(self.request, form.get_user())
        return redirect("rubrics_manage:index")

    def get_context_data(self, **kwargs):
        data = super(Login, self).get_context_data(**kwargs)
        data["page_title"] = u"Log in"
        return data


class ManageRubricsMixin(object):

    page_title = None

    def get_page_title(self):
        return self.page_title

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated():
            return redirect("rubrics_manage:login")
        elif not user.has_perm("rubrics.can_manage") and not user.is_superuser:
            return redirect("rubrics_manage:login")

        return super(ManageRubricsMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(ManageRubricsMixin, self).get_context_data(**kwargs)
        data["page_title"] = self.get_page_title()
        return data


class Index(ManageRubricsMixin, TemplateView):

    template_name = "rubrics/manage/index.html"
    page_title = u"Manage Evaluations"

    def get(self, request, *args, **kwargs):
        if request.is_ajax():

            return JsonResponse(dict(
            ))
        return super(Index, self).get(request, *args, **kwargs)
