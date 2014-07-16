#--------------------------------------------
# This is middleware to impersonate user
#--------------------------------------------

from django import http
from django.contrib.auth.models import User

class ImpersonateMiddleware(object):
    def process_request(self, request):
        if request.user.is_superuser and ('__impersonate' in request.GET or '__impersonate' in request.session):
            if "__impersonate" in request.GET:
                impersonate = request.GET['__impersonate']
            else:
                 impersonate = request.session['__impersonate']
                
            user = User.objects.filter(username=impersonate)
            if bool(user):
                request.user = user[0]
                if '__impersonate' in request.session and request.session['__impersonate'] != request.user.username:
                    del request.session['__impersonate']
                request.session['__impersonate'] = request.user.username
                request.session.modified = True  # Let's make sure...
            else:
                if '__impersonate' in request.session:
                    del request.session['__impersonate']

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