import os

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql_psycopg2'),
        'NAME': 'gadjo-test-%s' % os.environ.get('BRANCH_NAME', '').replace('/', '-')[:45],
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [],
            'builtins': [
                'gadjo.templatetags.gadjo',
            ],
        },
    },
]


DEBUG = True
USE_TZ = True
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'gadjo',
]
STATIC_URL = '/static/'
SITE_ID = 1
MIDDLEWARE_CLASSES = ()
LOGGING = {}
SECRET_KEY = 'yay'
