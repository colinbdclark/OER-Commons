from blog.models import Feed, Post
from django import forms
from django.conf import settings
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site
from django.utils.dateformat import format
import feedparser


class FeedForm(forms.ModelForm):

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get("url")
        if url:
            try:
                parsed = feedparser.parse(url)
                if not cleaned_data.get("title"):
                    cleaned_data["title"] = getattr(parsed.feed, "title", u"")
                if not cleaned_data.get("site_url"):
                    cleaned_data["site_url"] = getattr(parsed.feed, "link", u"")
            except:
                self._errors["url"] = self.error_class([u"Can't parse this URL."])
                del cleaned_data["url"]
        return cleaned_data

    class Meta:
        model = Feed
        fields = ["url", "title", "site_url"]


def harvested_on(feed):
    if not feed.harvested_on:
        return u"Not harvested yet."
    return format(feed.harvested_on, settings.DATETIME_FORMAT)


def posts_number(feed):
    return feed.posts.count()
posts_number.short_description = u"Posts"


class FeedAdmin(ModelAdmin):

    form = FeedForm
    list_display = ["title", posts_number, harvested_on]
    actions = ["harvest"]

    def harvest(self, request, queryset):
        cnt = 0
        for feed in queryset:
            cnt += feed.harvest()
        if cnt:
            self.message_user(request, u"%i new posts were harvested from selected feeds." % cnt)
        else:
            self.message_user(request, u"No new posts were harvested from selected feeds.")
    harvest.short_description = u"Harvest selected feeds"


class PostAdmin(ModelAdmin):

    list_display = ["title", "feed", "published_on"]
    list_filter = ["feed"]


site.register(Feed, FeedAdmin)
site.register(Post, PostAdmin)
