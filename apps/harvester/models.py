from django.db import models
from harvester.oaipmh.client import Client
from harvester.oaipmh.error import NoSetHierarchyError
from urllib2 import HTTPError


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
    
    base_url = models.URLField(max_length=200, verify_exists=False)
    name = models.CharField(max_length=200, null=True, blank=True)
    protocol_version = models.CharField(max_length=10, choices=PROTOCOL_VERSIONS, null=True, blank=True)
    earliest_datestamp = models.DateTimeField(null=True, blank=True)
    deleted_record = models.CharField(max_length=20, choices=DELETED_RECORDS, null=True, blank=True)
    granularity = models.CharField(max_length=20, choices=GRANULARITIES, null=True, blank=True)
    
    def __unicode__(self):
        return self.name or self.base_url
    
    class Meta:
        verbose_name = u"Repository"
        verbose_name_plural = u"Repositories"

    @property
    def client(self):
        return Client(self.base_url)

    def refresh(self):
        self._identify()
        self._get_metadata_prefixes()
        self._get_sets()
        
    def _identify(self):
        identify = self.client.identify()
        self.name = unicode(identify.repositoryName(), 'utf-8')
        self.protocol_version = unicode(identify.protocolVersion(), 'utf-8')
        AdminEmail.objects.filter(repository=self).delete()
        for email in identify.adminEmails():
            AdminEmail.objects.get_or_create(email=unicode(email, "utf-8"), repository=self)
        self.earliest_datestamp = identify.earliestDatestamp()
        if self.earliest_datestamp.year < 1900:
            self.earliest_datestamp = self.earliest_datestamp.replace(year=1900)
        if self.earliest_datestamp.month < 1:
            self.earliest_datestamp = self.earliest_datestamp.replace(month=1)
        if self.earliest_datestamp.day < 1:
            self.earliest_datestamp = self.earliest_datestamp.replace(day=1)
        self.deleted_record = unicode(identify.deletedRecord(), 'utf-8')
        self.granularity = unicode(identify.granularity(), 'utf-8')

    def _get_metadata_prefixes(self):
        MetadataPrefix.objects.filter(repository=self).delete()
        for prefix, schema, namespace in self.client.listMetadataFormats():
            MetadataPrefix.objects.get_or_create(prefix=unicode(prefix, "utf-8"),
                                                 schema=unicode(schema, "utf-8"),
                                                 namespace=unicode(namespace, "utf-8"),
                                                 repository=self,
                                                 ) 

    def _get_sets(self):
        Set.objects.filter(repository=self).delete()
        try:
            for spec, name, dummy in self.client.listSets():
                Set.objects.get_or_create(spec=unicode(spec),
                                          name=unicode(name),
                                          repository=self,
                                          ) 
        except NoSetHierarchyError:
            pass
        except HTTPError:
            pass
        

class Set(models.Model):
    
    repository = models.ForeignKey(Repository, related_name="sets")
    spec = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return u"%s - %s" % (self.spec, self.name)
    
    class Meta:
        ordering = ["repository", "spec", "name"]
    

class AdminEmail(models.Model):
    
    repository = models.ForeignKey(Repository, related_name="admin_emails")
    email = models.EmailField(max_length=200)

    def __unicode__(self):
        return self.email


class MetadataPrefix(models.Model):
    
    repository = models.ForeignKey(Repository, related_name="metadata_prefixes")
    prefix = models.CharField(max_length=30)
    schema = models.CharField(max_length=200)
    namespace = models.CharField(max_length=200)

    def __unicode__(self):
        return self.prefix
    
    class Meta:
        verbose_name = u"Metadata Prefix"
        verbose_name_plural = u"Metadata Prefixes"
        ordering = ["repository", "prefix"]
    

class Job(models.Model):
    
    repository = models.ForeignKey(Repository)
    metadata_prefix = models.ForeignKey(MetadataPrefix)
    from_date = models.DateField(null=True, blank=True)
    until_date = models.DateField(null=True, blank=True)
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
