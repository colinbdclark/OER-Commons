from curriculum.models import TaggedMaterial, AlignmentTag
from django.contrib.contenttypes.models import ContentType


def get_item_tags(item, user=None):

    content_type = ContentType.objects.get_for_model(item)

    user_tags = []
    if user and user.is_authenticated():
        for tagged in TaggedMaterial.objects.filter(content_type=content_type,
                                                    object_id=item.id,
                                                    user=user).select_related():
            tag = tagged.tag
            user_tags.append(dict(
                tag_id=tag.id,
                id=tagged.id,
                code=tag.full_code,
                url=tag.get_absolute_url(),
            ))

    item_tags = item.alignment_tags.all()
    tag_ids = set(item_tags.values_list("tag", flat=True).order_by().distinct())
    tag_ids = tag_ids - set([tag.pop("tag_id") for tag in user_tags])
    tags = []
    for tag in AlignmentTag.objects.filter(id__in=tag_ids):
        tags.append(dict(
            code=tag.full_code,
            url=tag.get_absolute_url(),
        ))

    return dict(tags=tags, user_tags=user_tags)

