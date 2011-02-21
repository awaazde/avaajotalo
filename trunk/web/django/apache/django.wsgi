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
import sys

sys.path.append('/home/dsc/Development')
sys.path.append('/home/dsc/Development/otalo')
sys.path.append('/usr/local/freeswitch/scripts/AO')
sys.path.append('/usr/local/freeswitch/scripts/AO/outbound')
sys.path.append('/usr/bin/ad_digest')

os.environ['DJANGO_SETTINGS_MODULE'] = 'otalo.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

