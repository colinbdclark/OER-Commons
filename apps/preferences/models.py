from django.contrib.auth.models import User
from django.db import models


# A list of all prefereces: {field_name: (cookie_name, default_value), ...}
PREFERENCE_FIELDS = {
    "show_toolbar": ("_pr_st", True),
}


class Preferences(models.Model):
    
    user = models.OneToOneField(User)
    
    show_toolbar = models.NullBooleanField(null=True, blank=True, default=None)
    
    def __unicode__(self):
        u"Preferences for %s" % unicode(self.user)