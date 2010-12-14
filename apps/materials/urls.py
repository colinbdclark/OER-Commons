from django.conf.urls.defaults import patterns, url, include
from materials.models.community import CommunityItem
from materials.models.course import Course
from materials.models.library import Library
from tags.urls import add_tags_patterns
from reviews.urls import add_review_patterns
from notes.urls import add_note_patterns
from saveditems.urls import saved_item_patterns
from rating.urls import rating_patterns


general_subject_patterns = patterns('materials.views',
    url(r"^/general_subject/(?P<general_subjects>[^/]+)/?$", "index.index", name="general_subject_index"),
)

grade_level_patterns = patterns('materials.views',
    url(r"^/edu_level/(?P<grade_levels>[^/]+)/?$", "index.index", name="grade_level_index"),
)

collection_patterns = patterns('materials.views',
    url(r"^/collection/(?P<collection>[^/]+)/?$", "index.index", name="collection_index"),
)

keyword_patterns = patterns('materials.views',
    url(r"^/keyword/(?P<keywords>[^/]+)/?$", "index.index", name="keyword_index"),
    url(r"^/tag/(?P<tags>[^/]+)/?$", "index.index", name="tag_index"), # TODO: set up redirect
    url(r"^/subject/(?P<subjects>[^/]+)/?$", "index.index", name="subject_index"), # TODO: set up redirect
)

license_patterns = patterns('materials.views',
    url(r"^/license/(?P<license>[^/]+)/?$", "index.index", name="license_index"),
)

browse_patterns = patterns('materials.views',
    url(r"^/?$", "index.index", name="index"),
) + \
general_subject_patterns + \
grade_level_patterns + \
collection_patterns + \
license_patterns + \
keyword_patterns


course_patterns = browse_patterns + patterns('materials.views',
    url(r"^/material_types/(?P<course_material_types>[^/]+)/?$", "index.index", name="material_type_index"),
    url(r"^/ocw/?$", "index.index", name="ocw_index", kwargs={"ocw": True}),
    url(r"^/(?P<course_or_module>full-course|learning-module)/?$", "index.index", name="course_or_module_index"),
    url(r"^/(?P<slug>[^/]+)/?$", "view_item.view_item", name="view_item"),
) + \
add_tags_patterns + \
add_review_patterns + \
add_note_patterns + \
saved_item_patterns + \
rating_patterns


library_patterns = browse_patterns + patterns('materials.views',
    url(r"^/material_types/(?P<library_material_types>[^/]+)/?$", "index.index", name="material_type_index"),
    url(r"^/(?P<slug>[^/]+)/?$", "view_item.view_item", name="view_item"),
) + \
add_tags_patterns + \
add_review_patterns + \
add_note_patterns + \
saved_item_patterns + \
rating_patterns

community_patterns = general_subject_patterns + \
grade_level_patterns + \
license_patterns + \
keyword_patterns + patterns('materials.views',
    url(r"^/oer_type/(?P<community_types>[^/]+)/?$", "index.index", name="community_type_index"),
    url(r"^/oer_topic/(?P<community_topics>[^/]+)/?$", "index.index", name="community_topic_index"),
    url(r"^/(?P<slug>[^/]+)/?$", "view_item.view_item", name="view_item"),
) + \
add_tags_patterns + \
add_review_patterns + \
add_note_patterns + \
saved_item_patterns + \
rating_patterns

microsite_browse_patterns = browse_patterns # TODO: add subtopic here

urlpatterns = patterns('materials.views',
    url(r"^oer/?$", "browse.browse", name="browse"),
    url(r"^oer/providers/?$", "browse.providers", name="browse_providers"),
    url(r"^browse", include(browse_patterns)),
    url(r"^search/?$", "index.index", name="search", kwargs={"search": True}),
    url(r"^courses", include(course_patterns, app_name="materials", namespace="courses"), {"model": Course}),
    url(r"^libraries", include(library_patterns, app_name="materials", namespace="libraries"), {"model": Library}),
    url(r"^community/?$", "browse.community", name="community"),
    url(r"^community", include(community_patterns, app_name="materials", namespace="community"), {"model": CommunityItem}),
    url(r"^(?P<microsite>[^/]+)/browse", include(microsite_browse_patterns)),
    url(r"^advanced-search/?$", "advanced_search.advanced_search", name="advanced_search"),
)

