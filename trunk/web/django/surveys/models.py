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
from django.db.models.query import CollectedObjects
from django.db.models.fields.related import ForeignKey
from datetime import datetime

class Subject(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)
    number = models.CharField(max_length=24)
    group = models.IntegerField(blank=True, null=True)
    
    def __unicode__(self):
        if self.name:
            return self.name + '-' + self.number + '-g' + str(self.group)
        else:
            return self.number+ '-g' + str(self.group)
    
class Survey(models.Model):
    name = models.CharField(max_length=128)
    complete_after = models.IntegerField(blank=True, null=True)
    dialstring_prefix = models.CharField(max_length=128, blank=True, null=True)
    dialstring_suffix = models.CharField(max_length=128, blank=True, null=True)
    number = models.CharField(max_length=24, blank=True, null=True)
    broadcast = models.BooleanField(default=False)
    # This is only relevant for inbound surveys. Make it a nullable for that reason.
    callback = models.NullBooleanField()
    
    TEMPLATE_DESIGNATOR = 'TEMPLATE'
    ANSWER_CALL_DESIGNATOR = 'AnswerCall'
    INBOUND_DESIGNATOR = 'INBOUND'
    template = models.BooleanField(default=False)
    
    STATUS_ACTIVE = 0
    STATUS_EXPIRED = 1
    STATUS_CANCELLED = 2
    status = models.IntegerField(default = 0);
    
    def getstatus(self):
        now = datetime.now()
        pendingcallcnt = Call.objects.filter(survey=self, date__gt=now).count()
        if pendingcallcnt == 0 and not self.status == Survey.STATUS_CANCELLED:
            self.status = Survey.STATUS_EXPIRED
            self.save()
        
        return self.status
    
    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return str(self.id)
    
    def deepcopy(self, newname):
        """
        Duplicate all related objects of `obj` setting
        `field` to `value`. If one of the duplicate
        objects has an FK to another duplicate object
        update that as well. Return the duplicate copy
        of `obj`.  
        """
        obj = self
        collected_objs = CollectedObjects()
        obj._collect_sub_objects(collected_objs)
        related_models = collected_objs.keys()
        root_obj = None
        # Traverse the related models in reverse deletion order.    
        for model in reversed(related_models):
            # Find all FKs on `model` that point to a `related_model`.
            fks = []
            for f in model._meta.fields:
                if isinstance(f, ForeignKey) and f.rel.to in related_models:
                    fks.append(f)
            # Replace each `sub_obj` with a duplicate.
            sub_obj = collected_objs[model]
            for pk_val, obj in sub_obj.iteritems():
                for fk in fks:
                    fk_value = getattr(obj, "%s_id" % fk.name)
                    # If this FK has been duplicated then point to the duplicate.
                    if fk_value in collected_objs[fk.rel.to]:
                        dupe_obj = collected_objs[fk.rel.to][fk_value]
                        setattr(obj, fk.name, dupe_obj)
                # Duplicate the object and save it.
                obj.id = None
                obj.save()
                if root_obj is None:
                    root_obj = obj
        setattr(root_obj, 'name', newname)
        return root_obj
    
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
    inputlen = models.IntegerField(blank=True, null=True)
    # In the future, when we want to display input results
    name = models.CharField(max_length=128, blank=True, null=True)
    
    def __unicode__(self):
        if self.name and self.name != '':
            return self.name + '-' + str(self.order)
        else:
            return self.file + '-' + unicode(self.survey) + '-' + str(self.order)
    
class Option(models.Model):
    # use string to represent no input value
    number = models.CharField(max_length=10)
    
    # Actions
    NEXT = 1
    PREV = 2
    REPLAY = 3
    GOTO = 4
    RECORD = 5
    INPUT = 6
    TRANSFER = 7;
    action = models.IntegerField()
    
    prompt = models.ForeignKey(Prompt)
    
class Param(models.Model):
    option = models.ForeignKey(Option)
    
    # For GOTO
    IDX = 'idx'   
    # For RECORD
    MAXLENGTH = 'maxlength'
    ONCANCEL = 'oncancel'
    MFID = 'mfid'
    CONFIRM_REC = 'confirm'
    # Foe TRANSFER
    NUM = 'num'
    
    name = models.CharField(max_length=24)
    
    value = models.CharField(max_length=128)
    
class Input(models.Model):
    # could be null if it's an incoming survey
    call = models.ForeignKey(Call, blank=True, null=True)
    prompt = models.ForeignKey(Prompt)
    # empty just in case we just want to record presence
    input = models.CharField(max_length=128, blank=True, null=True)
    