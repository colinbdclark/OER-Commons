from common.models import Language, Keyword
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import View
from oer.models import OER
from utils.decorators import login_required
import datetime


class New(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        oer, created = OER.objects.get_or_create(author=request.user,
                                                       is_new=True)
        profile = request.user.get_profile()
        if created:
            for level in profile.educator_student_levels.all():
                oer.student_levels.add(level)
            for subject in profile.educator_subjects.all():
                oer.keywords.add(Keyword.objects.get_or_create(name=subject.title)[0])
            oer.language = Language.objects.get(slug="en")
            oer.instruction_date = datetime.date.today() + datetime.timedelta(days=1)
            oer.save()

        return redirect("oer:edit_define", oer_id=oer.id)