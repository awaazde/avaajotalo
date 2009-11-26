from otalo.AO.models import Forum, Message, Message_forum, User
from django.contrib import admin

class MessageAdmin(admin.ModelAdmin):
    list_display = ('date', 'user')
    list_filter = ['date', 'user']
    search_fields = ['user']   

admin.site.register(Forum)
admin.site.register(User)
admin.site.register(Message, MessageAdmin)

