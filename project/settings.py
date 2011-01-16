import os

INTERNAL_IPS = ('127.0.0.1',)

DEFAULT_FROM_EMAIL = "info@oercommons.org"

TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'en'

LANGUAGES = (
    (u"en", u"English"),
)

DATE_FORMAT = "M j, Y"

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# Static file configuration
STATIC_ROOT = os.path.join(os.path.dirname(__file__), 'media')
STATIC_URL = MEDIA_URL
STATICFILES_EXCLUDED_APPS = (
    'project',
)
STATICFILES_MEDIA_DIRNAMES = (
    'media',
    'static',
)
STATICFILES_PREPEND_LABEL_APPS = (
    'django.contrib.admin',
)

ADMIN_MEDIA_ROOT = os.path.join(STATIC_ROOT, 'admin_media')
ADMIN_MEDIA_PREFIX = '/admin_media/'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'project.urls'


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.syndication',
    'django.contrib.sitemaps',
    'django_extensions',
    'south',
    'staticfiles',
    'compressor',
    'debug_toolbar',
    'haystack',
    'flatblocks',
    'mptt',
    'oauth_provider',
    'utils',
    'tags',
    'materials',
    'users',
    'rating',
    'reviews',
    'notes',
    'saveditems',
    'savedsearches',
    'myitems',
    'feedback',
    'information',
    'oai',
    'sendthis',
    'api',
    'project',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "django.core.context_processors.media",
    "staticfiles.context_processors.static_url",
)


AUTHENTICATION_BACKENDS = (
    'users.backend.BcryptBackend',
)

LOGIN_URL = '/login'
LOGOUT_URL = '/logout'
REDIRECT_FIELD_NAME = "next"

SITE_ID = 1

AUTH_PROFILE_MODULE = "users.Profile"

HAYSTACK_SITECONF = "project.search_sites"
HAYSTACK_SEARCH_ENGINE = "solr"
HAYSTACK_SOLR_URL = 'http://127.0.0.1:8983/solr/oercommons'

FLATBLOCKS_AUTOCREATE_STATIC_BLOCKS = True

AUTOSLUG_SLUGIFY_FUNCTION = "project.utils.slugify"

CACHE_VERSION = 1

OAUTH_AUTHORIZE_VIEW = "project.views.oauth_authorize"
OAUTH_CALLBACK_VIEW = "project.views.oauth_callback"
