from otalo.AO.models import Forum, Message, User
from django.contrib import admin

class MessageAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'forum')
    list_filter = ['date', 'user']
    search_fields = ['user']   

admin.site.register(Forum)
admin.site.register(Message, MessageAdmin)
admin.site.register(User)

