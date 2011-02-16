from django.db import models


PROTOCOL_VERSIONS = (
    ("2.0", "2.0"),
)


DELETED_RECORDS = (
    ("no", "No"),
    ("transient", "Transient"),
    ("persistent", "Persistent"),
)


GRANULARITIES = (
    ("YYYY-MM-DD", "YYYY-MM-DD"),
    ("YYYY-MM-DDThh:mm:ssZ", "YYYY-MM-DDThh:mm:ssZ"),
)


RUNNING = "running"
COMPLETE = "complete"
ERROR = "error"

STATUSES = (
    (RUNNING, u"Running"),
    (COMPLETE, u"Complete"),
    (ERROR, u"Error"),
)


class Repository(models.Model):
    
    base_url = models.URLField(max_length=200)
    name = models.CharField(max_length=200)
    protocol_version = models.CharField(max_length=10, choices=PROTOCOL_VERSIONS)
    earliest_datestamp = models.DateTimeField()
    deleted_record = models.CharField(max_length=20, choices=DELETED_RECORDS)
    granularity = models.CharField(max_length=20, choices=GRANULARITIES)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = u"Repository"
        verbose_name_plural = u"Repositories"


class Set(models.Model):
    
    repository = models.ForeignKey(Repository, related_name="sets")
    identifier = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    

class AdminEmail(models.Model):
    
    repository = models.ForeignKey(Repository, related_name="admin_emails")
    email = models.EmailField(max_length=200)


class MetadataPrefix(models.Model):
    
    repository = models.ForeignKey(Repository, related_name="metadata_prefixes")
    prefix = models.CharField(max_length=30)


class Job(models.Model):
    
    repository = models.ForeignKey(Repository)
    metadata_prefix = models.ForeignKey(MetadataPrefix)
    from_date = models.DateTimeField(null=True, blank=True)
    until_data = models.DateTimeField(null=True, blank=True)
    sets = models.ManyToManyField(Set, null=True, blank=True)
    email = models.EmailField(max_length=200)
    processed_records = models.IntegerField(null=True, blank=True)
    harvested_records = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateField(null=True, blank=True)
    
    def __unicode__(self):
        return unicode(self.repository)
    
    
class Error(models.Model):
    
    text = models.TextField()
    job = models.ForeignKey(Job, related_name="errors")  
