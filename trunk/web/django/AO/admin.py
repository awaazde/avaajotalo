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

from otalo.AO.models import Forum, Message, Message_forum, User, Tag, Responder_tag, Admin
from django.contrib import admin

class MessageAdmin(admin.ModelAdmin):
    list_display = ('date', 'user')
    list_filter = ['date', 'user']
    search_fields = ['user']   

admin.site.register(Forum)
admin.site.register(User)
admin.site.register(Message, MessageAdmin)
admin.site.register(Tag)
admin.site.register(Responder_tag)
admin.site.register(Admin)

