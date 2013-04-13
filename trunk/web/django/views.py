from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import render

'''
'    Django is not happy if you overload
'    the name 'logout' for a view
'''
def log_out(request):
    logout(request)
    referrer = request.META['HTTP_REFERER']
    referrer = referrer[referrer.find(settings.CONSOLE_ROOT)-1:]
    return render(request, 'registration/logged_out.html', {'referrer':referrer})
    