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

from django.conf.urls import *
from django.conf import settings
from longerusername.forms import AuthenticationForm

from registration.backends.default.views import RegistrationView
from awaazde.streamit.forms import CreateAcctForm

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^createaccount/$', RegistrationView.as_view(form_class=CreateAcctForm), name = 'registration_register'),
    (r'^', include('otalo.ao.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

   # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    url(r'^accounts/register/$', RegistrationView.as_view(form_class=CreateAcctForm), name = 'registration_register'),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^accounts/', include('django.contrib.auth.urls')),
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'authentication_form': AuthenticationForm}),
    (r'^accounts/password/reset/$','django.contrib.auth.views.password_reset', {'post_reset_redirect' : settings.PROJECT_MOUNT_POINT+'/accounts/password/reset/done/'}),
    (r'^accounts/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done'),
    (r'^accounts/password/reset/(?P<uidb64>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'django.contrib.auth.views.password_reset_confirm', {'post_reset_redirect' : settings.PROJECT_MOUNT_POINT+'/accounts/password/done/'}),
    (r'^accounts/password/done/$', 
        'django.contrib.auth.views.password_reset_complete'),
    (r'^logout/$', 'otalo.views.log_out'),
    (r'^captcha/', include('captcha.urls')),
)
