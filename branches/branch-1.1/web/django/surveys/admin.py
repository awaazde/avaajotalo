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

from otalo.surveys.models import Subject, Survey, Call, Prompt, Option, Input
from django.contrib import admin

class OrderingAdmin(admin.ModelAdmin):
    ordering = ('-id',)
    
class NameSearchAdmin(OrderingAdmin):
   search_fields = ['name', 'number']
   
class SurveyAdmin(NameSearchAdmin):
    exclude = ('subjects',)
   

class DateDisplayAdmin(OrderingAdmin):
    list_display = ('call', 'date', 'subject')
    
    def call(self, obj):
        return unicode(obj)

admin.site.register(Survey, SurveyAdmin)
admin.site.register(Subject, NameSearchAdmin)
admin.site.register(Call, DateDisplayAdmin)
admin.site.register(Prompt, OrderingAdmin)
admin.site.register(Option, OrderingAdmin)
admin.site.register(Input, OrderingAdmin)
