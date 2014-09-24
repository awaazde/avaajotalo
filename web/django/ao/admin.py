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

from otalo.ao.models import Forum, Message, User, Tag, Admin, Line, Message_forum, Forum_tag, Membership, Transaction, Forward, Dialer, Coupon
from django.contrib import admin

class OrderingAdmin(admin.ModelAdmin):
    ordering = ('-id',)

class ADAdmin(OrderingAdmin):
    raw_id_fields = ('user', 'auth_user', 'forum')


class MessageAdmin(OrderingAdmin):
    list_display = ('date', 'user')
    search_fields = ['user__name', 'user__number']
    raw_id_fields = ('user','thread')   

class UserAdmin(OrderingAdmin):
   search_fields = ['name', 'number']
   
class ForumTagInline(admin.TabularInline):
    ordering = ('-id',)
    model = Forum_tag
    extra = 1
    
class ForumAdmin(OrderingAdmin):
    inlines = (ForumTagInline,)
    search_fields = ['name']
    raw_id_fields = ('responders',)

class LineAdmin(OrderingAdmin):
    search_fields = ['name', 'number']

class MembershipAdmin(OrderingAdmin):
    raw_id_fields = ('user', 'group')
    readonly_fields = ('added','last_updated')

class MessageForumAdmin(OrderingAdmin):
    raw_id_fields = ('message', 'forum')
    
class TransactionAdmin(OrderingAdmin):
    raw_id_fields = ('user','call', 'coupon')
    readonly_fields = ('date',)

class CouponAdmin(OrderingAdmin):
    raw_id_fields = ('user',)

class DialerAdmin(OrderingAdmin):
    list_display = ('description', 'base_number', 'dialstring_prefix', 'country_code', 'machine_id')
    search_fields = ['description', 'dialstring_prefix']
    
admin.site.register(Forum, ForumAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Tag, OrderingAdmin)
admin.site.register(Admin, ADAdmin)
admin.site.register(Line, LineAdmin)
admin.site.register(Message_forum, MessageForumAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Forward, OrderingAdmin)
admin.site.register(Dialer, DialerAdmin)
admin.site.register(Coupon, CouponAdmin)