from urllib2 import URLError, HTTPError
from django import forms
from django.conf.urls.defaults import patterns, url
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site
from django.core.urlresolvers import reverse
from harvester.models import Repository, Job, ERROR, COMPLETE, NO_RECORDS_MATCH
from harvester.oaipmh.client import Client
from harvester.oaipmh.error import XMLSyntaxError
from harvester.views import add_job, job_errors, job_restart


class AddRepositoryForm(forms.ModelForm):

    def clean_base_url(self):

        base_url = self.cleaned_data["base_url"]

        # Drop the query string part
        base_url = base_url.split("?")[0]

        client = Client(base_url)
        try:
            client.identify()
        except (HTTPError, URLError):
            raise forms.ValidationError(
                u"Can't retrieve repository information from this URL. Make sure it's valid."
            )
        except XMLSyntaxError:
            raise forms.ValidationError(
                u"Unable to process the response from repository because it contains XML syntax error."
            )
        return base_url

    class Meta:
        fields = ["base_url"]
        model = Repository


class ChangeRepositoryForm(AddRepositoryForm):

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
        status = self.get_status_display()
        if self.status == ERROR:
            status = u"""<a href="%s">%s (%i)</a>""" % (reverse("admin:harvester_job_errors", args=(self.id,)),
                                                          status,
                                                          self.errors.count())
        if self.status in (COMPLETE, ERROR, NO_RECORDS_MATCH, None):
            if status is None:
                status = u""
            status += u""" - <a href="%s">restart</a>""" % reverse("admin:harvester_job_restart", args=(self.id,))
        return status
    status.allow_tags = True

    def download(self):
        if self.file:
            return u"""<a href="%s">Download</a>""" % self.file.url
        return u""
    download.allow_tags = True

    def set(self):
        set = self.set
        return set and set.name or u""

    def get_urls(self):
        urls = patterns("",
            url("^(\d+)/errors/$", self.admin_site.admin_view(job_errors), name="harvester_job_errors"),
            url("^(\d+)/restart/$", self.admin_site.admin_view(job_restart), name="harvester_job_restart"),
        )
        return urls + super(JobAdmin, self).get_urls()

    list_display = ["__unicode__", "metadata_prefix", set, status, "created_on",
                    "processed_records", download]

    def has_add_permission(self, request):\
        return False


site.register(Job, JobAdmin)
