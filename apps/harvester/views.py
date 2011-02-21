from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from harvester.models import Job, Repository, MetadataPrefix, Set, \
    METADATA_FORMATS


class HarvestForm(forms.ModelForm):

    repository = forms.ModelChoiceField(Repository.objects.all(),
                                        widget=forms.HiddenInput())
    email = forms.EmailField(widget=forms.TextInput(attrs={"class": "vTextField"}),
                             help_text=u"This email address is used to send the notification when harvesting is complete.")
    
    def __init__(self, *args, **kwargs):
        self.repository = kwargs.pop("repository")
        super(HarvestForm, self).__init__(*args, **kwargs)
        self.fields["metadata_prefix"].queryset = MetadataPrefix.objects.filter(repository=self.repository,
                                                                                prefix__in=METADATA_FORMATS.keys())
        self.fields["set"].queryset = Set.objects.filter(repository=self.repository)
    
    class Meta:
        model = Job
        fields = ["repository", "metadata_prefix", "from_date", "until_date",
                  "set", "email"]


def add_job(request, repository_id):
    repository_id = int(repository_id)
    repository = get_object_or_404(Repository, id=repository_id)
    repository_verbose_name_plural = repository._meta.verbose_name_plural
    initial = dict(repository=repository,
                   email=request.user.email)
    form = HarvestForm(initial=initial, repository=repository)
    
    if request.method == "POST":
        if "cancel" in request.POST:
            return HttpResponseRedirect(reverse("admin:harvester_repository_changelist"))

        form = HarvestForm(request.POST, initial=initial, repository=repository)
        
        if form.is_valid():
            job = form.save()
            job.run()
            return HttpResponseRedirect(reverse("admin:harvester_job_changelist"))
        
    title = u"Harvest"
    
    return direct_to_template(request, "harvester/harvest.html", locals())


def job_errors(request, job_id):
    job_id = int(job_id)
    job = get_object_or_404(Job, id=job_id)
    job_verbose_name_plural = job._meta.verbose_name_plural 
    errors = job.errors.all()
    if not errors.count():
        raise Http404()

    title = u"Job errors"
    
    return direct_to_template(request, "harvester/job-errors.html", locals())