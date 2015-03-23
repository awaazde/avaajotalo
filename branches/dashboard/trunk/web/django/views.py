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

from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import render

'''
'    Django is not happy if you overload
'    the name 'logout' for a view
'''
def log_out(request):
    logout(request)
    referrer = request.META.get('HTTP_REFERER',settings.CONSOLE_ROOT)
    referrer = referrer[referrer.find(settings.CONSOLE_ROOT):]
    return render(request, 'registration/logged_out.html', {'referrer':referrer})
    