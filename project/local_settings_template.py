from project.settings import *

DATABASES = {
    'default': {
        'NAME': '',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': '',
        'PASSWORD': ''
    },
}


ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# Don't share this with anybody.
SECRET_KEY = ''

FLAVOR = "oercommons"

BROKER_USER = ""
BROKER_PASSWORD = ""
BROKER_VHOST = "oercommons"

MAILCHIMP_API_KEY = ""
MAILCHIMP_LIST_ID = ""

LR_KEY = ""
LR_KEY_LOCATION = ""
LR_PASSPHRASE = ""
LR_NODE = ""

URL2PNG_KEY = ""
URL2PNG_SECRET = ""

GETSATISFACTION_KEY = ""
GETSATISFACTION_SECRET = ""

EMBEDLY_KEY = ""

YOUTUBE_DEV_KEY = ""
YOUTUBE_USERNAME = ""
YOUTUBE_PASSWORD = ""
YOUTUBE_SOURCE = ""
YOUTUBE_CLIENT_ID = ""
