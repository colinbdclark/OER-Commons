from autoslug.fields import AutoSlugField
from django.db import models
import BeautifulSoup
import datetime
import feedparser
import re


def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)


class Feed(models.Model):

    title = models.CharField(max_length=500, default=u"", blank=True)
    url = models.URLField(max_length=500)
    site_url = models.URLField(max_length=500, default=u"", blank=True)
    harvested_on = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.title or self.url

    def harvest(self, parsed=None):
        if parsed is None:
            parsed = feedparser.parse(self.url)
        cnt = 0
        for entry in parsed.entries:
            url = getattr(entry, 'link', None)
            if not url:
                continue
            identifier = getattr(entry, 'id', url)

            if self.posts.filter(identifier=identifier).count():
                continue

            title = entry.title
            try:
                text = entry.content[0].value
            except:
                text = getattr(entry, "summary", u"")

            snippet = getattr(entry, "summary", text)
            if snippet:
                snippet = remove_html_tags(snippet)

            if text:
                soup = BeautifulSoup.BeautifulSoup(text)
                for feedflare in soup.findAll("div", {"class": "feedflare"}):
                    feedflare.extract()
                text = unicode(soup)

            published_on = getattr(entry, "published_parsed", getattr(entry, "created_parsed", getattr(entry, "updated_parsed", None)))
            if published_on:
                published_on = datetime.datetime(*published_on[:6])
            else:
                published_on = datetime.datetime.now()

            Post(feed=self, title=title, text=text, snippet=snippet,
                url=url, identifier=identifier,
                published_on=published_on).save()

            cnt += 1

        self.harvested_on = datetime.datetime.now()
        self.save()

        return cnt


class Post(models.Model):

    title = models.CharField(max_length=1000)
    slug = AutoSlugField(max_length=1000, populate_from="title")
    feed = models.ForeignKey(Feed, related_name="posts")
    published_on = models.DateTimeField(null=True, blank=True)

    text = models.TextField(default=u"")
    snippet = models.TextField(default=u"")
    url = models.URLField(max_length=500)
    identifier = models.CharField(max_length=500)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ["published_on"]
