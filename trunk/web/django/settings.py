#===============================================================================
#    Copyright (c) 2009 Regents of the University of California, Stanford University, and others
# 
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
# 
#        http://www.apache.org/licenses/LICENSE-2.0
# 
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#===============================================================================
import os
from celery.schedules import crontab
# Django settings for otalo project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEVELOPMENT = True

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

# for security purposes
# should be set in production
ALLOWED_HOSTS = ['*']

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'otalo'             # Or path to database file if using sqlite3.
DATABASE_USER = 'otalo'             # Not used with sqlite3.
DATABASE_PASSWORD = 'otalo'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'otalo',
        'USER': 'otalo',
        'PASSWORD': 'otalo',
        'HOST': '',
        'PORT': '',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Kolkata'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/Users/neil/Development/media'
#MEDIA_ROOT = '/home/awaazde/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
#ADMIN_MEDIA_PREFIX = '/adminmedia2/'
STATIC_URL='/adminmedia/'
STATICFILES_DIRS = (
    "/Users/neil/Development/otalo/adminmedia",
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+1m4bqgx##tjp#rd4e=r#1ut=cw7xr3-za__oa3o8j377os_#='

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    #'django.template.loaders.filesystem.load_template_source',
    #'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'otalo.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/Users/neil/Development/workspace/django_templates',
    '/Users/neil/Development/workspace/ao/war',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
	'otalo.ao',
    'otalo.surveys',
    'otalo.sms',
    'django.contrib.admin',
    'kombu.transport.django',
    'south',
    'django_extensions',
    'django.contrib.staticfiles',
    'crispy_forms',
    'haystack',
    'streamit',
    'awaazde.console',
    'awaazde.xact',
    'rest_framework',
)

# this needs to go first
INSTALLED_APPS = ("longerusername",) + INSTALLED_APPS
MAX_USERNAME_LENGTH = 100

# Haystack Settings
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
        'INCLUDE_SPELLING': True
    },
}
HAYSTACK_LIMIT_TO_REGISTERED_MODELS = False
#HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# Celery Settings
BCAST_INTERVAL_MINS = 3
BROKER_URL = "django://"
#CELERY_ALWAYS_EAGER = True
#TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'
class CallsRouter(object):
    def route_for_task(self, task, args=None, kwargs=None):
        if task == 'otalo.surveys.tasks.schedule_call':
            dialer = args[1]
            machine_id = dialer.machine_id or ''
            return {'queue': 'calls'+str(machine_id)}
        return None
    
CELERY_ROUTES = (CallsRouter(), )
CELERYBEAT_SCHEDULE = {
    'schedule_by_dialerids': {
        'task': 'otalo.ao.tasks.schedule_bcasts_by_dialers',
        'schedule': crontab(minute='*/'+str(BCAST_INTERVAL_MINS), hour='8-21'),
        'args': (1,2,3,25,5,6,),
    },
    'response_calls': {
        'task': 'otalo.ao.tasks.response_calls',
        'schedule': crontab(minute='01', hour='8-21'),
        # interval_hours: should match how often the cron runs
        'args': (1,),
    },                   
    'gws_intl': {
        'task': 'otalo.ao.tasks.schedule_bcasts_by_basenums',
        'schedule': crontab(minute='*/'+str(BCAST_INTERVAL_MINS)),
        'args': (7961555000,),
    },
    'streams_bcasts': {
        'task': 'streamit.tasks.create_schedule_bcasts',
        'schedule': crontab(minute='*/'+str(BCAST_INTERVAL_MINS), hour='8-21'),
    },
    'create_xact_bcasts': {
        'task': 'xact.tasks.create_bcasts',
        'schedule': crontab(minute='*/'+str(BCAST_INTERVAL_MINS), hour='8-21'),
    },
}

STATIC_DOCUMENT_ROOT = '/Users/neil/Development/workspace/ao/war'

SERIALIZATION_MODULES = {
    'json': 'utils.serializers.custom_json'
}

CONSOLE_ROOT = '/AO'
PROJECT_MOUNT_POINT = ''
LOGIN_URL = PROJECT_MOUNT_POINT + '/accounts/login'
LOGOUT_URL = PROJECT_MOUNT_POINT + '/accounts/logout'
INBOUND_LOG_ROOT = '/Users/neil/Documents/inbound_'
OUTBOUND_LOG_ROOT = '/Users/neil/Documents/outbound_'
LOG_ROOT = '/Users/neil/Documents/'
CRISPY_TEMPLATE_PACK = 'bootstrap' 
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
REPORTS_ROOT = '/Users/neil/Documents/'
'''
'    For multi-server dialing setups. If you don't have multiple
'    servers making calls, you don't need to change this
'''
MACHINE_ID = None