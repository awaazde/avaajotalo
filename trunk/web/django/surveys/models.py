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

from django.db import models

class Subject(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)
    number = models.CharField(max_length=24)
    
    def __unicode__(self):
        if self.name:
            return self.name + '-' + self.number
        else:
            return self.number
    
class Survey(models.Model):
    name = models.CharField(max_length=128)
    complete_after = models.IntegerField(blank=True, null=True)
    dialstring_prefix = models.CharField(max_length=128, blank=True, null=True)
    dialstring_suffix = models.CharField(max_length=128, blank=True, null=True)
    # if this survey is tied to a phone number
    number = models.CharField(max_length=24, blank=True, null=True)
    
    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return str(self.id)
    
class Call(models.Model):
    subject = models.ForeignKey(Subject)
    survey = models.ForeignKey(Survey)
    date = models.DateTimeField()
    priority = models.IntegerField()
    complete = models.NullBooleanField(default=False)
    
    def __unicode__(self):
        return unicode(self.subject) + '-' + unicode(self.survey) + '-' + str(self.date) + '-p' + str(self.priority)
    
class Prompt(models.Model):
    file = models.CharField(max_length=128)
    order = models.IntegerField()
    bargein = models.BooleanField()
    survey = models.ForeignKey(Survey)
    delay = models.IntegerField(default=2000)
    
    def __unicode__(self):
        return self.file + '-' + unicode(self.survey) + '-' + str(self.order)
    
class Option(models.Model):
    # use string to represent no input value
    number = models.CharField(max_length=2)
    # corresponds to the constants in survey.lua
    action = models.IntegerField()
    action_param1 = models.CharField(max_length=128, blank=True, null=True)
    action_param2 = models.CharField(max_length=128, blank=True, null=True)
    prompt = models.ForeignKey(Prompt)
    