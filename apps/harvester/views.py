from autoslug.settings import slugify
from django import forms
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template
from harvester.models import Job, Repository, MetadataPrefix, Set, \
    METADATA_FORMATS, RSSFeed
from StringIO import StringIO
import csv
import datetime
import re
import htmlentitydefs


class HarvestForm(forms.ModelForm):

    repository = forms.ModelChoiceField(Repository.objects.all(),
                                        widget=forms.HiddenInput())
    email = forms.EmailField(widget=forms.TextInput(attrs={"class": "vTextField"}),
                             help_text=u"This email address is used to send the notification when harvesting is complete.")

    def __init__(self, *args, **kwargs):
        self.repository = kwargs.pop("repository")
        super(HarvestForm, self).__init__(*args, **kwargs)
        self.fields["metadata_prefix"].queryset = MetadataPrefix.objects.filter(repository=self.repository,
                                                                                prefix__in=METADATA_FORMATS.keys())
        self.fields["set"].queryset = Set.objects.filter(repository=self.repository)

    class Meta:
        model = Job
        fields = ["repository", "metadata_prefix", "from_date", "until_date",
                  "set", "email"]


def add_job(request, repository_id):
    repository_id = int(repository_id)
    repository = get_object_or_404(Repository, id=repository_id)
    repository_verbose_name_plural = repository._meta.verbose_name_plural
    initial = dict(repository=repository,
                   email=request.user.email)
    form = HarvestForm(initial=initial, repository=repository)

    if request.method == "POST":
        if "cancel" in request.POST:
            return redirect("admin:harvester_repository_changelist")

        form = HarvestForm(request.POST, initial=initial, repository=repository)

        if form.is_valid():
            job = form.save()
            job.run()
            return redirect("admin:harvester_job_changelist")

    title = u"Harvest"

    return direct_to_template(request, "harvester/harvest.html", locals())


def job_errors(request, job_id):
    job_id = int(job_id)
    job = get_object_or_404(Job, id=job_id)
    job_verbose_name_plural = job._meta.verbose_name_plural
    errors = job.errors.all()
    if not errors.count():
        raise Http404()

    title = u"Job errors"

    return direct_to_template(request, "harvester/job-errors.html", locals())


def job_restart(request, job_id):
    job_id = int(job_id)
    job = get_object_or_404(Job, id=job_id)
    job.processed_records = 0
    job.harvested_records = 0
    job.finished_on = None
    for error in job.errors.all():
        error.delete()
    job.file = None
    job.save()
    job.run()
    return redirect("admin:harvester_job_changelist")


def harvest_feed(request, feed_id):
    feed = get_object_or_404(RSSFeed, id=int(feed_id))
    feed.harvest()
    return redirect("admin:harvester_rssfeed_changelist")


##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)


def export_feed(request, feed_id, all_items=False):
    feed = get_object_or_404(RSSFeed, id=int(feed_id))

    items = feed.items.all() if all_items else feed.items.filter(exported=False)

    out = StringIO()
    writer = csv.writer(out, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(("CR_TITLE", "CR_URL", "CR_CREATE_DATE", "CR_ABSTRACT", "CR_KEYWORDS"))

    for row in items.values_list("title", "url", "date", "description", "keywords"):
        row = list(row)
        row[2] = row[2].date().isoformat() if row[2] else u""
        row = map(lambda x: unescape(x).encode("utf-8"), row)
        writer.writerow(row)

    feed_title = feed.title or "feed%s" % feed.id
    filename = "%s-%s.csv" % (slugify(feed_title), datetime.datetime.now().isoformat())

    out.seek(0)
    response = HttpResponse(out.read(), content_type="text/csv")
    response['Content-Disposition'] = 'inline;filename="%s"' % filename

    items.update(exported=True)

    return response
