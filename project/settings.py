import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

UNIT_TESTING = 'test' in sys.argv

DEBUG = True
ALLOWED_HOSTS = []
SECRET_KEY = 'test'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3' if UNIT_TESTING else 'db.sqlite3'
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
MIDDLEWARE_CLASSES = MIDDLEWARE  # Django 1.8 support

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',

    # Used for examples
    'project.photos',

    'daily_digest'
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ]
        }
    },
]

LOGIN_URL = '/admin/'

STATIC_URL = '/static/'

DAILY_DIGEST_CONFIG = {
    'title': 'Daily Digest',
    'from_email': 'support@test.com',
    'timezone': 'America/Los_Angeles',
    'exclude_today': False,
    'charts': [
        {
            'title': 'New Users',
            'model': 'django.contrib.auth.models.User',
            'date_field': 'date_joined',
            'filter_kwargs': {
                'is_active': True
            }
        },
        {
            'title': 'Photo Uploads',
            'model': 'project.photos.models.PhotoUpload',
            'date_field': 'created'
        }
    ]
}
