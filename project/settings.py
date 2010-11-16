import os


#DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#DATABASE_NAME = 'project.db'
#DATABASE_USER = ''             # Not used with sqlite3.
#DATABASE_PASSWORD = ''         # Not used with sqlite3.
#DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
#DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.


DATABASES = {
    'default': {
        'NAME': 'oercommons',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'postgres',
        'PASSWORD': 'PeOtipOtb9'
    },
    'old': {
        'NAME': 'oer',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'postgres',
        'PASSWORD': 'PeOtipOtb9'
    }
}


TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'en-us'

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
    'debug_toolbar.middleware.DebugToolbarMiddleware',
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
    'django_extensions',
    'south',
    'staticfiles',
    'compressor',
    'debug_toolbar',
    'haystack',
    'tags',
    'materials',
    'users',
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

SITE_ID = 1

AUTH_PROFILE_MODULE = "users.Profile"

HAYSTACK_SITECONF = "project.search_sites"
HAYSTACK_SEARCH_ENGINE = "solr"
HAYSTACK_SOLR_URL = 'http://127.0.0.1:8983/solr/oercommons'

