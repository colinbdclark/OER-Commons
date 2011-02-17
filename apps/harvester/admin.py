from django import forms
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site
from harvester.models import Repository, Job
from django.conf.urls.defaults import patterns, url
from harvester.views import add_job
from django.core.urlresolvers import reverse


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
    pass


site.register(Job, JobAdmin)