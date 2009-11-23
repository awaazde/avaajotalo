import os
import sys

sys.path.append('/home/dsc/Development')
sys.path.append('/home/dsc/Development/otalo')

os.environ['DJANGO_SETTINGS_MODULE'] = 'otalo.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

