from blog.models import Post, Feed
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template


def blog(request):

    page_title = u"Blog"
    breadcrumbs = [{"url": reverse("blog"), "title": page_title}]

    feeds = Feed.objects.all()

    posts = Post.objects.all().order_by("-published_on")
    if posts.count() > 20:
        posts = posts[:20]
    else:
        posts = posts[:]

    return direct_to_template(request, "blog/blog.html", locals())
