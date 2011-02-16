from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site
from harvester.models import Repository
from django import forms


class AddRepositoryForm(forms.ModelForm):
    
    class Meta:
        model = Repository


class RepositoryAdmin(ModelAdmin):
    
    readonly_fields = ["name", "protocol_version", "earliest_datestamp",
                       "deleted_record", "granularity"]


site.register(Repository, RepositoryAdmin)