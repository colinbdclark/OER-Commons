from dateutil.parser import parse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import connections
from django.db.utils import DatabaseError
from materials.models.common import Institution, Collection, Author, License, \
    Country, GeneralSubject, GradeLevel, Keyword, Language, GeographicRelevance, \
    MediaFormat
from materials.models.course import Course, RelatedMaterial, CourseMaterialType
from materials.utils import cleanup_keywords
from notes.models import Note
from rating.models import Rating
from reviews.models import Review
from saveditems.models import SavedItem
from tags.models import Tag
from users.models import Profile
from materials.models.material import reindex_materials


def force_unicode(o):
    if o is None:
        return None
    if isinstance(o, unicode):
        return o
    if isinstance(o, str):
        return o.decode("utf-8")
    if isinstance(o, list):
        return [force_unicode(item) for item in o]
    raise ValueError()


admin = User.objects.get(pk=1)
content_type = ContentType.objects.get_for_model(Course)


def run():
    courses = connections["old"].cursor()
    cursor = connections["old"].cursor()

    # Delete existing courses
    print "Removing existing courses..."
    Course.objects.all().delete()

    print "Creating courses..."

    cached_users = dict([(profile.principal_id, profile.user) for profile in Profile.objects.select_related().all()])
    cached_users["zope.manager"] = admin

    class_id = 100

    cursor.execute("SELECT object_id, id FROM _intids WHERE class_id = %s", [class_id])
    intids = dict(cursor.fetchall())

    tags_dict = {}
    cursor.execute("SELECT * FROM _tags")
    for item, principal, name, timestamp in cursor.fetchall():
        if item not in tags_dict:
            tags_dict[item] = []
        if principal in cached_users:
            tags_dict[item].append((name, cached_users[principal], timestamp))

    rating_dict = {}
    cursor.execute("SELECT * FROM _overall_rating WHERE id = 'overall_rating'")
    for item, id, principal, value, timestamp in cursor.fetchall():
        if item not in rating_dict:
            rating_dict[item] = []
        if principal in cached_users:
            rating_dict[item].append((int(value), cached_users[principal], timestamp))

    reviews_dict = {}
    cursor.execute("SELECT * FROM _reviews")
    for item, principal, text, timestamp in cursor.fetchall():
        if item not in reviews_dict:
            reviews_dict[item] = []
        if principal in cached_users:
            reviews_dict[item].append((text, cached_users[principal], timestamp))

    notes_dict = {}
    cursor.execute("SELECT * FROM _notes")
    for item, principal, text, timestamp in cursor.fetchall():
        if item not in notes_dict:
            notes_dict[item] = []
        if principal in cached_users:
            notes_dict[item].append((text, cached_users[principal], timestamp))

    saved_items_dict = {}
    cursor.execute("SELECT * FROM _bookmarks")
    for item, principal, timestamp in cursor.fetchall():
        if item not in saved_items_dict:
            saved_items_dict[item] = []
        if principal in cached_users:
            saved_items_dict[item].append((cached_users[principal], timestamp))

    creators = {}
    cursor.execute("SELECT * FROM _ownership WHERE class_id = %s", [class_id])
    for object_id, class_id, principal_id in cursor.fetchall():
        if principal_id in cached_users:
            creators[object_id] = cached_users[principal_id]
        else:
            creators[object_id] = admin

    created_dict = {}
    cursor.execute("SELECT * FROM _dublincore WHERE class_id = %s AND property = %s AND qualified = %s",
                   [class_id, "Date", "Created"])
    for id, object_id, class_id, property, qualified, value in cursor.fetchall():
        created_dict[object_id] = parse(value)

    modified_dict = {}
    cursor.execute("SELECT * FROM _dublincore WHERE class_id = %s AND property = %s AND qualified = %s",
                   [class_id, "Date", "Modified"])
    for id, object_id, class_id, property, qualified, value in cursor.fetchall():
        modified_dict[object_id] = parse(value)

    workflow_state_dict = {}
    cursor.execute("SELECT object_id, state FROM _workflowstates WHERE class_id = %s",
                   [class_id, ])
    for object_id, state in cursor.fetchall():
        workflow_state_dict[object_id] = state

    courses.execute("SELECT * FROM courses")

    total_items = courses.rowcount

    cnt = 0


    for id, name, title, description, content_creation_date, authors, \
        author_emails, author_countries, remote_url, keywords, \
        tech_requirements, general_subjects, grade_levels, languages, \
        geographic_relevance, institution, collection, material_types, \
        media_formats, curriculum_standards, course_or_module, \
        prerequisite_1_title, prerequisite_1_url, prerequisite_2_title, \
        prerequisite_2_url, postrequisite_1_title, postrequisite_1_url, \
        postrequisite_2_title, postrequisite_2_url, is_derived, derived_title, \
        derived_url, derived_why, course_id, iskme_id, cksum, native_id, \
        license_url, license_name, license_image, license_description, \
        copyright_holder, in_rss, rss_description, rss_datetime, is_featured, \
        publication_time, _searchindex, cou_bucket, tags in courses.fetchall():

        cnt += 1

        creator = creators[id]

        try:
            course = Course(id=id,
                            slug=force_unicode(name),
                            title=force_unicode(title),
                            abstract=force_unicode(description),
                            content_creation_date=content_creation_date,
                            url=force_unicode(remote_url),
                            tech_requirements=force_unicode(tech_requirements),
                            institution=institution and Institution.objects.get_or_create(name=force_unicode(institution))[0] or None,
                            collection=collection and Collection.objects.get_or_create(name=force_unicode(collection))[0] or None,
                            license=License.objects.get_or_create(url=force_unicode(license_url),
                                                                  name=force_unicode(license_name),
                                                                  image_url=force_unicode(license_image),
                                                                  description=force_unicode(license_description),
                                                                  copyright_holder=force_unicode(copyright_holder))[0],
                            curriculum_standards=curriculum_standards,
                            course_or_module=course_or_module,
                            course_id=force_unicode(course_id),
                            provider_id=force_unicode(native_id),
                            in_rss=in_rss,
                            rss_description=rss_description,
                            rss_timestamp=rss_datetime,
                            featured=is_featured,
                            published_on=publication_time,
                            creator=creator,
                            created_on=created_dict[id],
                            modified_on=modified_dict[id],
                            workflow_state=workflow_state_dict[id],
                            )
            course.save()
        except DatabaseError:
            import pprint
            pprint.pprint(dict([(k, len(v)) for k, v in locals().items() if isinstance(v, basestring) and len(v) > 100]))
            raise

        for i, author_name in enumerate(authors):
            author_name = force_unicode(author_name).replace(u'"', u"")
            author_email = len(author_emails) > i and force_unicode(author_emails[i]) or u""
            author_country = len(author_countries) > i and Country.objects.get(slug=force_unicode(author_countries[i])) or None
            course.authors.add(Author.objects.get_or_create(name=author_name,
                                                            email=author_email,
                                                            country=author_country)[0])

        if prerequisite_1_title:
            course.prerequisite_1 = RelatedMaterial.objects.get_or_create(title=force_unicode(prerequisite_1_title),
                                                                               url=force_unicode(prerequisite_1_url))[0]

        if prerequisite_2_title:
            course.prerequisite_2 = RelatedMaterial.objects.get_or_create(title=force_unicode(prerequisite_2_title),
                                                                               url=force_unicode(prerequisite_2_url))[0]

        if postrequisite_1_title:
            course.postrequisite_1 = RelatedMaterial.objects.get_or_create(title=force_unicode(postrequisite_1_title),
                                                                               url=force_unicode(postrequisite_1_url))[0]

        if postrequisite_2_title:
            course.postrequisite_2 = RelatedMaterial.objects.get_or_create(title=force_unicode(postrequisite_2_title),
                                                                               url=force_unicode(postrequisite_2_url))[0]

        if is_derived:
            course.derived_from = RelatedMaterial.objects.get_or_create(title=force_unicode(derived_title),
                                                                               url=force_unicode(derived_url),
                                                                               description=force_unicode(derived_why))[0]

        for o in general_subjects:
            course.general_subjects.add(GeneralSubject.objects.get(slug=o))

        for o in grade_levels:
            course.grade_levels.add(GradeLevel.objects.get(slug=o))


        cleaned_keywords = cleanup_keywords(force_unicode(keywords))

        for o in cleaned_keywords:
            course.keywords.add(Keyword.objects.get_or_create(name=o)[0])

        for o in languages:
            course.languages.add(Language.objects.get(slug=o))

        for o in geographic_relevance:
            course.geographic_relevance.add(GeographicRelevance.objects.get(slug=o))

        for o in material_types:
            course.material_types.add(CourseMaterialType.objects.get(slug=o))

        for o in media_formats:
            course.media_formats.add(MediaFormat.objects.get(slug=o))

        int_id = intids[id]

        if int_id in tags_dict:
            for name, user, timestamp in tags_dict[int_id]:
                tag = Tag(object_id=id, content_type=content_type,
                    name=force_unicode(name), user=user)
                tag.timestamp = timestamp
                tag.save()

        if int_id in rating_dict:
            for value, user, timestamp in rating_dict[int_id]:
                rating = Rating(object_id=id, content_type=content_type,
                       value=value, user=user)
                rating.timestamp = timestamp
                rating.save()

        if int_id in reviews_dict:
            for text, user, timestamp in reviews_dict[int_id]:
                review = Review(object_id=id, content_type=content_type,
                                text=force_unicode(text), user=user)
                review.timestamp = timestamp
                review.save()

        if int_id in notes_dict:
            for text, user, timestamp in notes_dict[int_id]:
                note = Note(object_id=id, content_type=content_type,
                       text=force_unicode(text), user=user)
                note.timestamp = timestamp
                note.save()

        if int_id in saved_items_dict:
            for user, timestamp in saved_items_dict[int_id]:
                saved_item = SavedItem(object_id=id, content_type=content_type,
                          user=user)
                saved_item.timestamp = timestamp
                saved_item.save()

        if cnt % 100 == 0:
            print "%i of %i" % (cnt, total_items)

    reindex_materials()
    print "Done!"
