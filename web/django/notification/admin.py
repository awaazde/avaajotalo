from otalo.notification.models import Notification, NotificationUser, Setting
from otalo.notification.models import NotificationMessage
from django.contrib import admin

admin.site.register(Notification)
admin.site.register(NotificationUser)
admin.site.register(Setting)
admin.site.register(NotificationMessage)

