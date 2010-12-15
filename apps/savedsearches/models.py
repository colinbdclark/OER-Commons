from django.contrib.auth.models import User
from django.db import models


class SavedSearch(models.Model):

    user = models.ForeignKey(User)
    title = models.CharField(max_length=500)
    url = models.CharField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = u"Saved Search"
        verbose_name_plural = u"Saved Searches"
        ordering = ["timestamp"]

    def __unicode__(self):
        return "'%s' by %s" % (self.title, self.user)

    def get_absolute_url(self):
        return self.url
