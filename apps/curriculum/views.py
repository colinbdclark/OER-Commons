from annoying.decorators import ajax_request
from curriculum.models import TaggedMaterial, AlignmentTag, Standard, Grade, \
    LearningObjectiveCategory
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from haystack.exceptions import NotRegistered
from haystack.sites import site
from utils.decorators import login_required


class TagResourceForm(forms.Form):
    
    tag = forms.ModelChoiceField(queryset=AlignmentTag.objects.all())
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop("instance", None)
        self.user = kwargs.pop("user", None)
        super(TagResourceForm, self).__init__(*args, **kwargs)

    def save(self):
        tag = self.cleaned_data.get("tag")
        if not self.instance or not self.user or not tag:
            return
        content_type = ContentType.objects.get_for_model(self.instance)
        object_id = self.instance.id
        tagged, created = TaggedMaterial.objects.get_or_create(user=self.user,
                                                     tag=tag,
                                                     content_type=content_type,
                                                     object_id=object_id)
        return tagged


@login_required
@ajax_request
def align(request, app_label, model, object_id):

    if request.method != "POST":
        raise Http404()
        
    content_type = get_object_or_404(ContentType, app_label=app_label,
                                     model=model)
    model = content_type.model_class()
    object_id = int(object_id)
    
    item = get_object_or_404(model, id=object_id)
    user = request.user

    form = TagResourceForm(request.POST, instance=item, user=user)
    if form.is_valid():
        tagged = form.save()
        tag = form.cleaned_data["tag"]

        try:
            site.update_object(item)
        except NotRegistered:
            pass
        
        return dict(status="success",
                    tag=dict(id=tagged.id, code=tag.full_code,
                             url=reverse("materials:alignment_index",
                                        kwargs=dict(alignment=tag.full_code))))
    else:
        return dict(status="error")
    

@login_required
@ajax_request
def list_user_tags(request, app_label, model, object_id):

    content_type = get_object_or_404(ContentType, app_label=app_label,
                                     model=model)
    model = content_type.model_class()
    object_id = int(object_id)
        
    tags = []
    for tagged in TaggedMaterial.objects.filter(content_type=content_type,
                                                object_id=object_id,
                                                user=request.user).select_related():
        tag = tagged.tag
        tags.append(dict(id=tagged.id, code=tag.full_code,
                         url=reverse("materials:alignment_index",
                                     kwargs=dict(alignment=tag.full_code))))

    return dict(tags=tags)


@login_required
@ajax_request
def delete_tag(request):
    if request.method != "POST":
        raise Http404()
    
    try:
        tagged = TaggedMaterial.objects.get(id=int(request.POST["id"]))
    except:
        return dict(status="error")
    
    tagged.delete()
    return dict(status="success")
    
    
@ajax_request    
def list_standards(request, existing=False):
    if existing:
        ids = TaggedMaterial.objects.all().values_list("tag__standard", flat=True).order_by().distinct()
    else:
        ids = AlignmentTag.objects.values_list("standard", flat=True).order_by().distinct()
    return dict(options=list(Standard.objects.filter(id__in=ids).values("id", "name")))


@ajax_request
def list_grades(request, existing=False):
    standard = request.POST.get("standard")
    try:
        standard = Standard.objects.get(id=int(standard))
    except:
        return HttpResponse(u"", status=400)

    if existing:
        ids = TaggedMaterial.objects.filter(tag__standard=standard).values_list("tag__grade", flat=True).order_by().distinct()
    else:
        ids = AlignmentTag.objects.filter(standard=standard).values_list("grade", flat=True).order_by().distinct() 
    return dict(options=list(Grade.objects.filter(id__in=ids).values("id", "name")))


@ajax_request
def list_categories(request, existing=False):
    standard = request.POST.get("standard")
    try:
        standard = Standard.objects.get(id=int(standard))
    except:
        return HttpResponse(u"", status=400)
    
    grade = request.POST.get("grade")
    try:
        grade = Grade.objects.get(id=int(grade))
    except:
        return HttpResponse(u"", status=400)

    if existing:
        ids = TaggedMaterial.objects.filter(tag__standard=standard,
                                            tag__grade=grade).values_list("tag__category", flat=True).order_by().distinct()
    else:
        ids = AlignmentTag.objects.filter(standard=standard,
                                          grade=grade).values_list("category",
                                                                   flat=True).order_by().distinct() 
    return dict(options=list(LearningObjectiveCategory.objects.filter(id__in=ids).values("id", "name")))


@ajax_request
def list_tags(request, existing=False):
    standard = request.POST.get("standard")
    try:
        standard = Standard.objects.get(id=int(standard))
    except:
        return HttpResponse(u"", status=400)
    
    grade = request.POST.get("grade")
    try:
        grade = Grade.objects.get(id=int(grade))
    except:
        return HttpResponse(u"", status=400)

    category = request.POST.get("category")
    try:
        category = LearningObjectiveCategory.objects.get(id=int(category))
    except:
        return HttpResponse(u"", status=400)

    if existing:
        ids = TaggedMaterial.objects.filter(tag__standard=standard,
                                            tag__grade=grade,
                                            tag__category=category).values_list("tag", flat=True).order_by().distinct()
        tags = AlignmentTag.objects.filter(id__in=ids)
    else:
        tags = AlignmentTag.objects.filter(standard=standard, grade=grade,
                                           category=category) 
    
    optgroups = []
    items = []
    title = None
    
    # Group tag by subcategory and create the following structure:
    # tag1.subcategory
    # - tag1
    # - tag2 (has the same subcat as tag1)
    # - tag3 (has the same subcat as tag2)
    # tag4.subcategory
    # - tag4
    # - tag5 (has the same subcat as tag4)
    # ....
    
    for tag in tags:
        if tag.subcategory != title:
            # Start filling the next optgroup
            if title and items:
                optgroups.append(dict(title=title, items=items))
            title = tag.subcategory
            items = []
        items.append(dict(id=tag.id,
                          name=unicode(tag),
                          code=tag.full_code))
        
    if title and items:
        # Add the last optgroup to final results
        optgroups.append(dict(title=title, items=items))
        
    return dict(optgroups=optgroups)


def get_tag_description(request, standard, grade, category, code):
    tag = get_object_or_404(AlignmentTag,
                            standard__code=standard,
                            grade__code=grade,
                            category__code=category,
                            code=code)

    return direct_to_template(request,
                              "curriculum/tag-description-tooltip.html",
                              dict(tag=tag))