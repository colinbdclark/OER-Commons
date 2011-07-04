from django.db import models
from django.db.models.aggregates import Max
from materials.models.microsite import Microsite


class Slide(models.Model):

    title = models.CharField(max_length=200)
    html = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True,
                              upload_to="upload/slider")
    url = models.URLField(null=True, blank=True)
    microsite = models.ForeignKey(Microsite, null=True, blank=True)
    order = models.IntegerField(default=0)

    def __unitode__(self):
        return self.title

    class Meta:
        ordering = ["microsite", "order"]

    def save(self, *args, **kwargs):
        if not self.order:
            max_order = Slide.objects.filter(
                             microsite=self.microsite).aggregate(
                                             Max("order"))["order__max"] or 0
            self.order = max_order + 1
        super(Slide, self).save(*args, **kwargs)
