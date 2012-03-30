from curriculum.models import Standard, LearningObjectiveCategory, \
    AlignmentTag
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site


site.register(Standard, ModelAdmin)
site.register(LearningObjectiveCategory, ModelAdmin)
site.register(AlignmentTag, ModelAdmin)
