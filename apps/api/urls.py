from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("api.views",
   url("^search/?$", "search.search"),
   url("^getTags/?$", "get_tags.get_tags"),
   url("^setTags/?$", "set_tags.set_tags"),
   url("^getReview/?$", "get_review.get_review"),
   url("^setReview/?$", "set_review.set_review"),
   url("^getRating/?$", "get_rating.get_rating"),
   url("^setRating/?$", "set_rating.set_rating"),
   url("^addCourse/?$", "add_course.add_course"),
   url("^addLibrary/?$", "add_library.add_library"),
   url("^addMatter/?$", "add_community_item.add_community_item"),
)
