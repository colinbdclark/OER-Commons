from annoying.decorators import ajax_request
from autoslug.settings import slugify
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from haystack.sites import site
from tags.models import Tag
from utils.decorators import login_required


@login_required
@ajax_request
def add(request, app_label, model, object_id):

    content_type = get_object_or_404(ContentType, app_label=app_label,
                                     model=model)
    model = content_type.model_class()
    object_id = int(object_id)
    
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
    
    return response


@login_required
@ajax_request
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

    return response
    
    
@login_required
@ajax_request
def get_tags(request, app_label, model, object_id):
    
    content_type = get_object_or_404(ContentType, app_label=app_label,
                                     model=model)
    model = content_type.model_class()
    object_id = int(object_id)
    
    item = get_object_or_404(model, id=object_id)
    user = request.user

    user_tags = []
    for id, slug, name in item.tags.filter(user=user).values_list("id", "slug", "name"):
        user_tags.append(dict(id=id,
                              url=reverse("materials:keyword_index",
                                         kwargs={"keywords": slug}),
                              name=name))
        
    item_tags = item.tags.all()
    if user_tags:
        item_tags = item_tags.exclude(id__in=[t["id"] for t in user_tags])

    item_tags = item_tags.values_list("slug", "name")
    item_tags = [dict(url=reverse("materials:keyword_index",
                                  kwargs={"keywords": slug}),
                      name=name) for slug, name in item_tags]
    
    response = dict(tags=item_tags,
                    user_tags=user_tags)

    return response
    
    
    