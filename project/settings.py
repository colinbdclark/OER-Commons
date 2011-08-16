import djcelery
import os
import time
import sys


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
STATICFILES_STORAGE = 'staticfiles.storage.StaticFileStorage'
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

ADMIN_MEDIA_ROOT = os.path.join(STATIC_ROOT, 'admin')
ADMIN_MEDIA_PREFIX = os.path.join(STATIC_URL, 'admin') + "/"

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'preferences.middleware.PreferencesMiddleware',
    'depiction.middleware.ProfilerMiddleware',
    'abtesting.middleware.ABTestingMiddleware',
    'users.middleware.ConfirmationMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
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
    'haystack_scheduled',
    'flatblocks',
    'mptt',
    'indexer',
    'paging',
    'sentry',
    'sentry.client',
    'djcelery',
    'oauth_provider',
    'honeypot',
    'mailchimp',
    'sorl.thumbnail',
    'django_coverage',
    'utils',
    'abtesting',
    'common',
    'tags',
    'geo',
    'curriculum',
    'materials',
    'users',
    'rating',
    'reviews',
    'saveditems',
    'savedsearches',
    'myitems',
    'feedback',
    'information',
    'oai',
    'sendthis',
    'api',
    'reports',
    'stats',
    'slider',
    'harvester',
    'visitcounts',
    'newsletter',
    'preferences',
    'rubrics',
    'project',
)

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "django.core.context_processors.media",
    "django.core.context_processors.debug",
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

CACHES = {
    'default': {
        'BACKEND': 'cache_utils.group_backend.CacheClass',
        'LOCATION': '127.0.0.1:11211',
    },
}

CACHE_VERSION = 1

OAUTH_AUTHORIZE_VIEW = "project.views.oauth_authorize"
OAUTH_CALLBACK_VIEW = "project.views.oauth_callback"

CACHE_MIDDLEWARE_SECONDS = 60
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True


BROKER_HOST = "localhost"
BROKER_PORT = 5672

djcelery.setup_loader()


HONEYPOT_FIELD_NAME = "address"

# Honeypot value is current time as int
HONEYPOT_VALUE = lambda: int(time.time())

def honeypot_verifier(value):
    try:
        value = int(value)
    except:
        return False
    # Check the difference between current time moment and honeypot value.
    # It must be positive and less than one hour.
    now = int(time.time())
    diff = now - value
    if diff < 0 or diff > 3600:
        return False
    return True

HONEYPOT_VERIFIER = honeypot_verifier

DEFAULT_AVATAR = STATIC_URL + "images/default-avatar.png"
AVATAR_SIZE = 140
GRAVATAR_BASE = "http://www.gravatar.com/avatar"

WEBKIT2PNG_EXECUTABLE = None

if sys.platform == "darwin":
    WEBKIT2PNG_EXECUTABLE = "/System/Library/Frameworks/Python.framework/Versions/2.6/bin/python %s -W %%(width)i -H %%(height)i -o %%(filename)s %%(url)s" % os.path.join(os.path.dirname(__file__), "webkit2png_osx.py")
elif sys.platform == "linux2":
    WEBKIT2PNG_EXECUTABLE = "python %s -x %%(width)i %%(height)i -g %%(width)i %%(height)i -F javascript -o %%(filename)s %%(url)s" % os.path.join(os.path.dirname(__file__), "webkit2png_linux.py")

COVERAGE_REPORT_HTML_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'coverage')

