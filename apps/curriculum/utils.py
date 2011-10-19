from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg
from rubrics.models import StandardAlignmentScore


def get_item_tags(item, user=None):

    tags = {}

    if user and user.is_authenticated():
        for tagged in item.alignment_tags.filter(user=user).select_related():
            tag = tagged.tag
            tags[tag.id] = dict(
                id=tagged.id,
                code=tag.full_code,
                url=tag.get_absolute_url(),
                score=None,
            )

    for tagged in item.alignment_tags.all().select_related():
        tag = tagged.tag
        if tag.id not in tags:
            tags[tag.id] = dict(
                code=tag.full_code,
                url=tag.get_absolute_url(),
                score=None,
            )

    content_type = ContentType.objects.get_for_model(item)

    for row in StandardAlignmentScore.objects.filter(
        evaluation__content_type=content_type,
        evaluation__object_id=item.id,
        alignment_tag__id__in=tags.keys(),
    ).values("alignment_tag__id").annotate(score=Avg("score__value")):
        tags[row["alignment_tag__id"]]["score"] = row["score"]

    tags = sorted(tags.values(), key=lambda x: x["score"], reverse=True)
    for tag in tags:
        del tag["score"]

    return tags

