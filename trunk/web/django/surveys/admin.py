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

from otalo.surveys.models import Subject, Survey, Call, Prompt, Option
from django.contrib import admin

class NameSearchAdmin(admin.ModelAdmin):
   search_fields = ['name', 'number']

class DateDisplayAdmin(admin.ModelAdmin):
    list_display = ('call', 'date', 'subject')
    
    def call(self, obj):
        return unicode(obj)

admin.site.register(Survey, NameSearchAdmin)
admin.site.register(Subject, NameSearchAdmin)
admin.site.register(Call, DateDisplayAdmin)
admin.site.register(Prompt)
admin.site.register(Option)

