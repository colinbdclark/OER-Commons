from autoslug.settings import slugify
from celery.decorators import task
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.files.base import File
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils.dateformat import format
from harvester.metadata.oai_dc import OAI_DC
from harvester.oaipmh.client import Client
from harvester.oaipmh.error import NoSetHierarchyError, NoRecordsMatchError
from tempfile import NamedTemporaryFile
from urllib2 import HTTPError
import csv
import datetime
import traceback


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
NO_RECORDS_MATCH = "no-records"

STATUSES = (
    (RUNNING, u"Running"),
    (COMPLETE, u"Complete"),
    (ERROR, u"Error"),
    (NO_RECORDS_MATCH, u"No records match"),
)


METADATA_FORMATS = {
    "oai_dc": OAI_DC()
}


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
    harvested_on = models.DateTimeField(null=True, blank=True)
    
    def __unicode__(self):
        s = u"%s - %s" % (self.spec, self.name)
        if self.harvested_on:
            s = u"%s - Harvested on %s" % (s, format(self.harvested_on,
                                                     settings.DATETIME_FORMAT))
        return s
    
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
    

@task()
def run_job(job):
    job.status = RUNNING
    job.save()
    metadata_prefix = job.metadata_prefix.prefix
    format = METADATA_FORMATS[metadata_prefix]
    client = job.repository.client
    client.ignoreBadCharacters(True)
    client.updateGranularity()
    
    kwargs = {}
    kwargs['metadataPrefix'] = metadata_prefix 
    if job.from_date:
        kwargs['from_'] = job.from_date.replace(tzinfo=None) # Remove timezone information
    if job.until_date:
        kwargs['until'] = job.until_date.replace(tzinfo=None) # Remove timezone information

    if job.set:
        kwargs["set"] = job.set.spec

    f = NamedTemporaryFile()
    writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)

    writer.writerow(format.header)

    job.harvested_records = 0
    job.processed_records = 0
    
    try:
        for header, metadata, about in client.listRecords(**kwargs):
            if header.isDeleted():
                continue
            identifier = str(header.identifier())
            try:
                writer.writerow(format.process_record(identifier, metadata))
                job.harvested_records += 1
            except:
                text = u"Error while processing record identifier: %s\n%s" % (identifier,
                                                                              traceback.format_exc())
                Error(text=text, job=job).save()
            job.processed_records += 1
            
            # Save the job after every 100 processed records
            if not job.processed_records % 100:
                job.save()
        
        if job.errors.count():
            job.status = ERROR
        else:
            job.status = COMPLETE
            
        now = datetime.datetime.now()
        
        if job.set:
            job.set.harvested_on = now
            job.set.save()
            
        job.finished_on = now

        filename_parts = [slugify(unicode(job.repository))]
        if job.set:
            filename_parts.append(slugify(job.set.spec))
        filename_parts.append(now.isoformat())
        filename = "-".join(filename_parts) + ".csv"
        job.file.save(filename, File(f))        

    except NoRecordsMatchError:
        job.status = NO_RECORDS_MATCH

    except:
        job.status = ERROR
        Error(text=traceback.format_exc(), job=job).save()
        
    finally:
        job.save()
        f.close()

    job.notify()
    

class Job(models.Model):
    
    repository = models.ForeignKey(Repository)
    metadata_prefix = models.ForeignKey(MetadataPrefix)
    from_date = models.DateField(null=True, blank=True)
    until_date = models.DateField(null=True, blank=True)
    set = models.ForeignKey(Set, null=True, blank=True)
    email = models.EmailField(max_length=200)
    processed_records = models.IntegerField(null=True, blank=True)
    harvested_records = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUSES,
                              null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    finished_on = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to="harvester",
                            null=True, blank=True)
    
    def __unicode__(self):
        return unicode(self.repository)
    
    def run(self):
        run_job.delay(self)
    
    def notify(self):
        base_url = "http://%s" % Site.objects.get_current().domain
        text = render_to_string("harvester/notification.html",
                                dict(base_url=base_url, job=self))
        send_mail(u"Harvesting job is complete",
                  text, settings.DEFAULT_FROM_EMAIL, [self.email])
    
    class Meta:
        verbose_name = u"Job"
        verbose_name_plural = u"Jobs"
    
    
class Error(models.Model):
    
    text = models.TextField()
    job = models.ForeignKey(Job, related_name="errors")  
