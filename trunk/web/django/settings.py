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
MEDIA_URL = 'http://awaaz.de/console/'

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
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'utils.middleware.ImpersonateMiddleware',
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
    'registration',
    'awaazde.streamit',
    'awaazde.console',
    'awaazde.xact',
    'corsheaders',
    'rest_framework',
    'rest_framework_swagger',
    'rest_framework.authtoken',
    'awaazde.payment',
    'captcha'
)

ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window; we can use a different value.
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge'
CAPTCHA_LETTER_ROTATION = None
CAPTCHA_FONT_SIZE = 32

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
class ADRouter(object):
    def route_for_task(self, task, args=None, kwargs=None):
        if task == 'otalo.surveys.tasks.schedule_call':
            dialer = args[1]
            machine_id = dialer.machine_id or ''
            return {'queue': 'calls'+str(machine_id)}
        elif task == 'otalo.ao.tasks.cache_audio':
            # get the main machine_id
            machine_id = args[1][0] if args[1] is not None else ''
            return {'queue': 'audio_cache'+str(machine_id)}
        return None

CELERY_ROUTES = (ADRouter())
CELERYBEAT_SCHEDULE = {
    'schedule_by_dialerids': {
        'task': 'otalo.ao.tasks.schedule_bcasts_by_dialers',
        'schedule': crontab(minute='*/'+str(BCAST_INTERVAL_MINS), hour='8-21'),
        'args': (1,2,3,25,5,6,),
    },
    'response_calls': {
        'task': 'otalo.ao.tasks.response_calls',
        'schedule': crontab(minute='01', hour='8-21'),
        # interval_mins: should match how often the cron runs
        'args': (60,),
    },      
    'convert_audio': {
        'task': 'otalo.ao.tasks.convert_audio',
        'schedule': crontab(minute='*/10', hour='8-21'),
        # interval_mins: should match how often the cron runs
        'args': (10,),
    },   
    'update_search_index': {
        'task': 'otalo.ao.tasks.update_search_index',
        'schedule': crontab(minute='01', hour='7,19'),
        # interval_hours: should match how often the cron runs
        'args': (12,),
    },           
    'gws_intl': {
        'task': 'otalo.ao.tasks.schedule_bcasts_by_basenums',
        'schedule': crontab(minute='*/'+str(BCAST_INTERVAL_MINS)),
        'args': (7961555000,),
    },
    'streams_create_bcasts': {
        'task': 'awaazde.streamit.tasks.create_bcasts',
        'schedule': crontab(minute='*/'+str(BCAST_INTERVAL_MINS)),
    },
    'streams_schedule_bcasts': {
        'task': 'awaazde.streamit.tasks.schedule_all_bcasts',
        'schedule': crontab(minute='*/'+str(BCAST_INTERVAL_MINS), hour='8-21'),
    },
}

STATIC_DOCUMENT_ROOT = '/Users/neil/Development/workspace/ao/war'

SERIALIZATION_MODULES = {
    'json': 'utils.serializers.custom_json'
}

CORS_ORIGIN_WHITELIST = ('awaaz.de', 'classlynx.co') #allowing classlynx

CORS_ALLOW_HEADERS = (
        'x-requested-with',
        'content-type',
        'accept',
        'origin',
        'Authorization',
        'x-csrftoken'
)

REST_FRAMEWORK = {
    'PAGINATE_BY': 100,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',  
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # optional
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '500/day',
    }
}

CONSOLE_ROOT = '/AO'
PROJECT_MOUNT_POINT = ''
LOGIN_URL = PROJECT_MOUNT_POINT + '/accounts/login'
LOGOUT_URL = PROJECT_MOUNT_POINT + '/accounts/logout'
INBOUND_LOG_ROOT = '/Users/neil/Documents/inbound_'
OUTBOUND_LOG_ROOT = '/Users/neil/Documents/outbound_'
LOG_ROOT = '/Users/neil/Documents/'
CRISPY_TEMPLATE_PACK = 'bootstrap' 
EMAIL_HOST_USER = 'signup@awaaz.de'
EMAIL_HOST_PASSWORD = 'awaaz123'
DEFAULT_FROM_EMAIL = 'Awaaz.De Team <signup@awaaz.de>'
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "signup@awaaz.de"
EMAIL_HOST_PASSWORD = 'xxx'
DEFAULT_FROM_EMAIL = 'Awaaz.De Team <signup@awaaz.de>'
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
REPORTS_ROOT = '/Users/neil/Documents/'
#Config for payment gateway
PAYMENT_GATEWAY_CONFIG = {
    'account_id': '5880',   #This is a test id. Actual account id needs to be put in prod
    'secret_key': 'ebskey', #This is a test key.Actual secret key needs to be put in prod
    'action_url': 'https://secure.ebs.in/pg/ma/sale/pay', #Action url where payment request needs to be submitted
    'return_url': 'https://awaazde/console/payment/pay/', #url where payment response would be returened by payment gateway
    'mode'      : 'TEST', # or on prod 'LIVE' its transaction mode
}

SWAGGER_SETTINGS = {
    "api_path": CONSOLE_ROOT,
}

'''
'    For multi-server dialing setups. If you don't have multiple
'    servers making calls, you don't need to change this
'''
MACHINE_ID = None



