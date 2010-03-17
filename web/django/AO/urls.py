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
    (r'^tags/$', 'otalo.AO.views.tags'),
    (r'^messagetag/(?P<message_id>\d+)/$', 'otalo.AO.views.messagetag'),
)

if settings.DEVELOPMENT:
    urlpatterns += patterns('', 
        (r'^(?P<path>.*\.(css|js|html|jpg|png|gif|swf))$', 'django.views.static.serve',
            {'document_root': settings.STATIC_DOCUMENT_ROOT}),
        (r'^(?P<path>.*\.(mp3|wav))$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
