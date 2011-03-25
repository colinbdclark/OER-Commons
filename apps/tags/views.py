from autoslug.settings import slugify
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from haystack.sites import site
from tags.models import Tag
from utils.decorators import login_required
import cjson


@login_required
def add(request, content_type_id=None, object_id=None):

    if not content_type_id or not object_id:
        raise Http404()
    
    content_type_id = int(content_type_id)
    object_id = int(object_id)
    
    content_type = get_object_or_404(ContentType, id=content_type_id)
    model = content_type.model_class()
    item = get_object_or_404(model, id=object_id)
    user = request.user

    new_tags = []

    if request.method == "POST":
        tags = [t.strip() for t in request.POST.get("tags", u"").split(u",")]
        for tag in tags:
            if not item.tags.filter(user=user, slug=slugify(tag)).count():
                tag = Tag(content_type=content_type, object_id=object_id,
                    user=user, name=tag)
                tag.save()
                new_tags.append(tag)
               
    site.update_object(item)
    
    response = {}
    response["tags"] = []
    for tag in new_tags:
        response["tags"].append(dict(name=tag.name,
                                     id=tag.id,
                                     url=reverse("materials:keyword_index",
                                                 kwargs={"keywords": tag.slug}),
                                     ))
    
    return HttpResponse(cjson.encode(response), content_type="application/json")


@login_required
def delete(request):
    
    response = {}
    
    if request.method == "POST":
        try:
            id = int(request.POST.get("id"))
        except:
            id = None
        if id:
            try:
                tag = Tag.objects.get(id=id, user=request.user)
                item = tag.content_object
                tag.delete()
                site.update_object(item)
            except Tag.DoesNotExist:
                pass

    return HttpResponse(cjson.encode(response), content_type="application/json")
    