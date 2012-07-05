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

from otalo.ao.models import Forum, Message, User, Tag, Admin, Line, Message_forum, Forum_tag, Membership
from django.contrib import admin

class OrderingAdmin(admin.ModelAdmin):
    ordering = ('-id',)

class MessageAdmin(OrderingAdmin):
    list_display = ('date', 'user')
    list_filter = ['date', 'user']
    search_fields = ['user__name', 'user__number']   

class UserAdmin(OrderingAdmin):
   search_fields = ['name', 'number']
   
class ForumTagInline(admin.TabularInline):
    ordering = ('-id',)
    model = Forum_tag
    extra = 1
    
class ForumAdmin(OrderingAdmin):
    inlines = (ForumTagInline,)

admin.site.register(Forum, ForumAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Tag, OrderingAdmin)
admin.site.register(Admin, OrderingAdmin)
admin.site.register(Line, OrderingAdmin)
admin.site.register(Message_forum, OrderingAdmin)
admin.site.register(Membership, OrderingAdmin)

