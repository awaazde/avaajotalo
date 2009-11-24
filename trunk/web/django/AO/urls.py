from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'otalo.AO.views.index'),
    (r'^forum/$', 'otalo.AO.views.forum'),
    (r'^messages/(?P<forum_id>\d+)/$', 'otalo.AO.views.messages'),
    (r'^message/(?P<message_id>\d+)/$', 'otalo.AO.views.message'),
    (r'^user/(?P<user_id>\d+)/$', 'otalo.AO.views.user'),
    (r'^update/message/$', 'otalo.AO.views.updatemessage'),
    (r'^move/$', 'otalo.AO.views.movemessage'),
    (r'^upload/$', 'otalo.AO.views.uploadmessage'),
    (r'^thread/(?P<message_id>\d+)/$', 'otalo.AO.views.thread'),
)

if settings.DEVELOPMENT:
    urlpatterns += patterns('', 
        (r'^(?P<path>.*\.(css|js|html|jpg|png|gif|swf))$', 'django.views.static.serve',
            {'document_root': settings.STATIC_DOCUMENT_ROOT}),
        (r'^(?P<path>.*\.(mp3|wav))$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
