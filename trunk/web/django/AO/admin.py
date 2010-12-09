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

from otalo.AO.models import Forum, Message, User, Tag, Admin, Line, Message_forum, Forum_tag
from django.contrib import admin

class MessageAdmin(admin.ModelAdmin):
    list_display = ('date', 'user')
    list_filter = ['date', 'user']
    search_fields = ['user__name', 'user__number']   

class UserAdmin(admin.ModelAdmin):
   search_fields = ['name', 'number']
   
class ForumTagInline(admin.TabularInline):
    model = Forum_tag
    extra = 1
    
class ForumAdmin(admin.ModelAdmin):
    inlines = (ForumTagInline,)

admin.site.register(Forum, ForumAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Tag)
admin.site.register(Admin)
admin.site.register(Line)
admin.site.register(Message_forum)

