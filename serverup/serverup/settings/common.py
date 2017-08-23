import sys
from os.path import abspath, basename, dirname, join, normpath

from django.contrib import admin

DEBUG = False
ALLOWED_HOSTS = ['*']

PAYPAL_TEST = True
PAYPAL_RECEIVER_EMAIL = 'hi-facilitator@nuidi.com'

### ADMINS CONFIG ###############################

admin.site.site_header = 'ServerUP'
admin.site.site_title = 'ServerUP'
admin.site.index_title = 'ServerUP'


ADMINS = (
    'Doggra', 'doggra@protonmail.com',
)

MANAGERS = ADMINS

### PATHS CONFIG ################################

LOGIN_URL = '/login/'

DJANGO_ROOT = dirname(dirname(abspath(__file__)))
PROJECT_ROOT = dirname(DJANGO_ROOT)
SITE_NAME = basename(DJANGO_ROOT)
STATIC_ROOT = join(PROJECT_ROOT, 'run', 'static')
MEDIA_ROOT = join(PROJECT_ROOT, 'run', 'media')

STATICFILES_DIRS = [
    join(PROJECT_ROOT, 'static'),
]

PROJECT_TEMPLATES = [
    join(PROJECT_ROOT, 'templates'),
]

### APPS CONFIG #################################

DEFAULT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap',
    'userland',
    'server',
    'serverup',
    'history',
    'paypal.standard.ipn',
]

### MIDDLEWARES CONFIG  #########################

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
]

### TEMPLATES CONFIG ############################

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': PROJECT_TEMPLATES,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

### RUNNING CONFIGURATION

SITE_ID = 1
WSGI_APPLICATION = '%s.wsgi.application' % SITE_NAME
ROOT_URLCONF = '%s.urls' % SITE_NAME
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

### INTERNATIONALIZATION

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = False

### CELERY

CELERY_IMPORTS = ('server',)

### SECRET KEY ##################################

# We store secret key in a file
SECRET_FILE = normpath(join(PROJECT_ROOT, 'run', 'SECRET.key'))

# Get or create secret key
try:
    SECRET_KEY = open(SECRET_FILE).read().strip()
except IOError:
    try:
        from django.utils.crypto import get_random_string
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!$%&()=+-_'
        SECRET_KEY = get_random_string(50, chars)
        with open(SECRET_FILE, 'w') as f:
            f.write(SECRET_KEY)
    except IOError:
        raise Exception('Could not open %s for writing!' % SECRET_FILE)
