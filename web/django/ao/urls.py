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

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'otalo.ao.views.index'),
    (r'^forum/$', 'otalo.ao.views.forum'),
    (r'^messages/(?P<forum_id>\d+)/$', 'otalo.ao.views.messages'),
    (r'^messageforum/(?P<message_forum_id>\d+)/$', 'otalo.ao.views.messageforum'),
    (r'^user/(?P<user_id>\d+)/$', 'otalo.ao.views.user'),
    (r'^update/message/$', 'otalo.ao.views.updatemessage'),
    (r'^update/status/(?P<action>\w+)/$', 'otalo.ao.views.updatestatus'),
    (r'^move/$', 'otalo.ao.views.movemessage'),
    (r'^recordorupload/$', 'otalo.ao.views.record_or_upload_message'),
    (r'^thread/(?P<message_forum_id>\d+)/$', 'otalo.ao.views.thread'),
    (r'^tags/$', 'otalo.ao.views.tags'),
    (r'^tags/(?P<forum_id>\d+)/$', 'otalo.ao.views.tags'),
    (r'^tagsbyline/(?P<line_id>\d+)/$', 'otalo.ao.views.tagsbyline'),
    (r'^messagetag/(?P<message_forum_id>\d+)/$', 'otalo.ao.views.messagetag'),
    (r'^responders/(?P<forum_id>\d+)/$', 'otalo.ao.views.responders'),
    (r'^messageresponder/(?P<message_forum_id>\d+)/$', 'otalo.ao.views.messageresponder'),
    (r'^moderator/$', 'otalo.ao.views.moderator'),
    (r'^line/$', 'otalo.ao.views.line'),
    (r'^download/(?P<model>\w+)/(?P<model_id>\d+)/$', 'otalo.ao.views.download'),
    (r'^survey/$', 'otalo.ao.views.survey'),
    (r'^bcast/$', 'otalo.ao.views.bcast'),
    (r'^fwdthread/(?P<message_forum_id>\d+)/$', 'otalo.ao.views.forwardthread'),
    (r'^surveyinput/(?P<survey_id>\d+)/$', 'otalo.ao.views.surveyinput'),
    (r'^promptresponses/(?P<prompt_id>\d+)/$', 'otalo.ao.views.promptresponses'),
    (r'^cancelsurvey/(?P<survey_id>\d+)/$', 'otalo.ao.views.cancelsurvey'),
    (r'^surveydetails/(?P<survey_id>\d+)/$', 'otalo.ao.views.surveydetails'),
    (r'^regularbcast/$', 'otalo.ao.views.regularbcast'),
    (r'^sms/(?P<line_id>\d+)/$', 'otalo.ao.views.sms'),
    (r'^smsrecipients/(?P<smsmsg_id>\d+)/$', 'otalo.ao.views.smsrecipients'),
    (r'^sendsms/$', 'otalo.ao.views.sendsms'),
    (r'^smsin/$', 'otalo.ao.views.smsin'),
    (r'^group/$', 'otalo.ao.views.group'),
    (r'^search/$', 'otalo.ao.views.search'),
    # s is for streams views
    (r'^s/', include('awaazde.streamit.urls')),
    # 2 is for gen2 console views
    (r'^2/', include('awaazde.console.urls')),
    (r'^payment/', include('awaazde.payment.urls')),
    (r'^xact/', include('awaazde.xact.urls')),
    (r'^xact-auth/', include('rest_framework.urls', namespace='rest_framework')),
)

if settings.DEVELOPMENT:
    urlpatterns += patterns('', 
        (r'^(?P<path>.*\.(css|js|html|jpg|png|gif|swf))$', 'django.views.static.serve',
            {'document_root': settings.STATIC_DOCUMENT_ROOT}),
        (r'^(?P<path>.*\.(mp3|wav))$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
