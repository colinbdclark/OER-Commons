from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site
from harvester.models import Repository
from django import forms


class AddRepositoryForm(forms.ModelForm):
    
    base_url = forms.URLField(verify_exists=False)
    
    class Meta:
        fields = ["base_url"]
        model = Repository


class ChangeRepositoryForm(forms.ModelForm):
    
    class Meta:
        model = Repository


class RepositoryAdmin(ModelAdmin):
    
    readonly_fields = ["name", "protocol_version", "earliest_datestamp", "deleted_record", "granularity"]
    list_display = ["name", "base_url", ]
    
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


site.register(Repository, RepositoryAdmin)