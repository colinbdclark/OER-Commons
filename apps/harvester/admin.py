from django import forms
from django.conf.urls.defaults import patterns, url
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site
from django.core.urlresolvers import reverse
from harvester.models import Repository, Job, ERROR
from harvester.views import add_job, job_errors


class AddRepositoryForm(forms.ModelForm):
    
    base_url = forms.URLField(verify_exists=False)
    
    class Meta:
        fields = ["base_url"]
        model = Repository


class ChangeRepositoryForm(forms.ModelForm):
    
    class Meta:
        model = Repository


class RepositoryAdmin(ModelAdmin):
    
    readonly_fields = ["name", "protocol_version", "earliest_datestamp",
                       "deleted_record", "granularity"]
    list_display = ["name", "base_url", "harvest"]
    
    def harvest(self, obj):
        return """<a href="%s">Harvest</a>""" % reverse("admin:harvester_add_job", args=(obj.id,))
    harvest.allow_tags = True
    
    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = ChangeRepositoryForm
        else:
            self.form = AddRepositoryForm
        return super(RepositoryAdmin, self).get_form(request, obj=obj, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        if not obj.pk:
            obj.save()
        obj.refresh()
        obj.save()
        
    def get_urls(self):
        urls = patterns("",
            url("^(\d+)/harvest/$", self.admin_site.admin_view(add_job), name="harvester_add_job"),
        )
        return urls + super(RepositoryAdmin, self).get_urls()


site.register(Repository, RepositoryAdmin)


class JobAdmin(ModelAdmin):

    def status(self):
        if self.status == ERROR:
            return """<a href="%s">%s (%i)</a>""" % (reverse("admin:harvester_job_errors", args=(self.id,)), 
                                                     self.get_status_display(),
                                                     self.errors.count())
        return self.get_status_display()
    status.allow_tags = True

    def get_urls(self):
        urls = patterns("",
            url("^(\d+)/errors/$", self.admin_site.admin_view(job_errors), name="harvester_job_errors"),
        )
        return urls + super(JobAdmin, self).get_urls()

    list_display = ["__unicode__", "metadata_prefix", status, "created_on",
                    "processed_records"]

    def has_add_permission(self, request):\
        return False
    

site.register(Job, JobAdmin)