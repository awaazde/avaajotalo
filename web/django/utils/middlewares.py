#--------------------------------------------
# This is middleware to impersonate user
#--------------------------------------------

from django import http
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User

class ImpersonateMiddleware(object):
    def process_request(self, request):
        if request.user.is_superuser and ('__impersonate' in request.GET or '__impersonate' in request.session):
            if "__impersonate" in request.GET:
                impersonate = request.GET['__impersonate']
            else:
                 impersonate = request.session['__impersonate']
                
            user = get_object_or_404(User, username=impersonate)
            
            request.user = user
            if '__impersonate' in request.session and request.session['__impersonate'] != request.user.username:
                del request.session['__impersonate']
            request.session['__impersonate'] = request.user.username
            request.session.modified = True  # Let's make sure...
        elif request.user.is_superuser:
            if request.get_full_path() == settings.CONSOLE_ROOT or request.get_full_path() == settings.CONSOLE_ROOT + "/":
                raise PermissionDenied()

    def process_response(self, request, response):
        if not hasattr(request, 'user'):
            return response
        
        if request.user.is_superuser and ('__impersonate' in request.GET or '__impersonate' in request.session):
            if "__impersonate" in request.GET:
                impersonate = request.GET['__impersonate']
            else:
                 impersonate = request.session['__impersonate']
            
            if isinstance(response, http.HttpResponseRedirect):
                location = response["Location"]
                if "?" in location:
                    location += "&"
                else:
                    location += "?"
                location += "__impersonate=%s" % impersonate
                response["Location"] = location
        return response