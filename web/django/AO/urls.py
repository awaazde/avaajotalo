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

from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'otalo.AO.views.index'),
    (r'^forum/$', 'otalo.AO.views.forum'),
    (r'^messages/(?P<forum_id>\d+)/$', 'otalo.AO.views.messages'),
    (r'^messageforum/(?P<message_forum_id>\d+)/$', 'otalo.AO.views.messageforum'),
    (r'^user/(?P<user_id>\d+)/$', 'otalo.AO.views.user'),
    (r'^update/message/$', 'otalo.AO.views.updatemessage'),
    (r'^update/status/(?P<action>\w+)/$', 'otalo.AO.views.updatestatus'),
    (r'^move/$', 'otalo.AO.views.movemessage'),
    (r'^upload/$', 'otalo.AO.views.uploadmessage'),
    (r'^thread/(?P<message_forum_id>\d+)/$', 'otalo.AO.views.thread'),
    (r'^tags/(?P<forum_id>\d+)/$', 'otalo.AO.views.tags'),
    (r'^messagetag/(?P<message_forum_id>\d+)/$', 'otalo.AO.views.messagetag'),
    (r'^responders/(?P<forum_id>\d+)/$', 'otalo.AO.views.responders'),
    (r'^messageresponder/(?P<message_forum_id>\d+)/$', 'otalo.AO.views.messageresponder'),
    (r'^username/$', 'otalo.AO.views.username'),
    (r'^line/$', 'otalo.AO.views.line'),
    (r'^download/(?P<model>\w+)/(?P<model_id>\d+)/$', 'otalo.AO.views.download'),
    (r'^survey/$', 'otalo.AO.views.survey'),
    (r'^bcast/$', 'otalo.AO.views.bcast'),
    (r'^fwdthread/(?P<message_forum_id>\d+)/$', 'otalo.AO.views.forwardthread'),
    (r'^surveyinput/(?P<survey_id>\d+)/$', 'otalo.AO.views.surveyinput'),
    (r'^promptresponses/(?P<prompt_id>\d+)/$', 'otalo.AO.views.promptresponses'),
    (r'^cancelsurvey/(?P<survey_id>\d+)/$', 'otalo.AO.views.cancelsurvey'),
    (r'^surveydetails/(?P<survey_id>\d+)/$', 'otalo.AO.views.surveydetails'),
)

if settings.DEVELOPMENT:
    urlpatterns += patterns('', 
        (r'^(?P<path>.*\.(css|js|html|jpg|png|gif|swf))$', 'django.views.static.serve',
            {'document_root': settings.STATIC_DOCUMENT_ROOT}),
        (r'^(?P<path>.*\.(mp3|wav))$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
