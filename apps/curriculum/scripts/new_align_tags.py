from annoying.functions import get_object_or_None

def run():
    import csv, os
    from curriculum.models import Grade, AlignmentTag, TaggedMaterial
    from haystack_scheduled.indexes import Indexed

    tags = {}
    for standard,  old_full_code, grade, cat, code, subcat, desc in csv.reader(open(os.path.join(os.path.dirname(__file__), "new-tags.csv"))):

        # Create new grades
        if not Grade.objects.filter(code=grade).exists():
            Grade.objects.create(code=grade, name=u"%s Grades" % grade)

        tags[old_full_code] = dict(grade=grade,
                                   category=cat,
                                   code=code,
                                   subcategory=subcat,
                                   description=desc)

    tagged_materials_updated = 0
    tags_removed = 0

    for tag in AlignmentTag.objects.all().select_related():
        if tag.full_code not in tags:
            continue

        d = tags[tag.full_code]

        if tag.grade.code != d["grade"]:
            try:
                existing = AlignmentTag.objects.get_by_natural_key(
                    d["grade"],
                    d["category"],
                    d["code"]
                )
                for tagged in TaggedMaterial.objects.filter(tag=tag):
                    try:
                        item = tagged.content_object
                    except AttributeError:
                        item = None
                    if TaggedMaterial.objects.filter(tag=existing, user=tagged.user,
                                                     content_type=tagged.content_type,
                                                     object_id=tagged.object_id).exists():
                        tagged.delete()
                    else:
                        tagged.tag = existing
                        tagged.save()
                    if isinstance(item, Indexed):
                        item.reindex()
                    tagged_materials_updated += 1
                tag.delete()
                tags_removed += 1
                continue
            except AlignmentTag.DoesNotExist:
                tag.grade = Grade.objects.get(code=d["grade"])

        tag.subcategory = d["subcategory"]
        tag.code = d["code"]
        tag.description = d["description"]
        tag.save()

    print "Tagged materials updated:", tagged_materials_updated
    print "Tags removed:", tags_removed

    # Remove tags with K-12 grade
    grade = get_object_or_None(Grade, code=u"K-12")
    if grade:
        print "Removing K-12 grade..."
        tagged_materials_removed = 0
        tags_removed = 0
        for tag in AlignmentTag.objects.filter(grade=grade):
            for tagged in TaggedMaterial.objects.filter(tag=tag):
                try:
                    item = tagged.content_object
                except AttributeError:
                    item = None
                tagged.delete()
                if isinstance(item, Indexed):
                    item.reindex()
                tagged_materials_removed += 1
            tag.delete()
            tags_removed += 1
        grade.delete()
        print "Tagged materials removed:", tagged_materials_removed
        print "Tags removed:", tags_removed

