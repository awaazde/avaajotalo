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
from django.db.models.deletion import Collector
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
    
    # Used to identify calls that were made to inbound surveys
    # (could be done with inbound_designator, but this is more correct)
    inbound = models.NullBooleanField()
    
    TEMPLATE_DESIGNATOR = 'TEMPLATE'
    ANSWER_CALL_DESIGNATOR = 'AnswerCall'
    
    # Deprecated: use inbound field instead
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
    
    def deepcopy(self, newname, value=None, field=None, duplicate_order=None):
        """
        Duplicate all related objects of obj setting
        field to value. If one of the duplicate
        objects has an FK to another duplicate object
        update that as well. Return the duplicate copy
        of obj.
        duplicate_order is a list of models which specify how
        the duplicate objects are saved. For complex objects
        this can matter. Check to save if objects are being
        saved correctly and if not just pass in related objects
        in the order that they should be saved.
        """
        obj = self
        collector = Collector({})
        collector.collect([obj])
        collector.sort()
        related_models = collector.data.keys()
        data_snapshot =  {}
        for key in collector.data.keys():
            data_snapshot.update({ key: dict(zip([item.pk for item in collector.data[key]], [item for item in collector.data[key]])) })
        root_obj = None
    
        # Sometimes it's good enough just to save in reverse deletion order.
        if duplicate_order is None:
            duplicate_order = reversed(related_models)
    
        for model in duplicate_order:
            # Find all FKs on model that point to a related_model.
            fks = []
            for f in model._meta.fields:
                if isinstance(f, ForeignKey) and f.rel.to in related_models:
                    fks.append(f)
            # Replace each `sub_obj` with a duplicate.
            if model not in collector.data:
                continue
            sub_objects = collector.data[model]
            for obj in sub_objects:
                for fk in fks:
                    fk_value = getattr(obj, "%s_id" % fk.name)
                    # If this FK has been duplicated then point to the duplicate.
                    fk_rel_to = data_snapshot[fk.rel.to]
                    if fk_value in fk_rel_to:
                        dupe_obj = fk_rel_to[fk_value]
                        setattr(obj, fk.name, dupe_obj)
                # Duplicate the object and save it.
                obj.id = None
                if field is not None:
                    setattr(obj, field, value)
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
    # the prompt to be played is based on input from some other prompt
    dependson = models.ForeignKey('self', blank=True, null=True)
    
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
    TRANSFER = 7
    
    action = models.IntegerField()
    
    prompt = models.ForeignKey(Prompt)
    
class Param(models.Model):
    option = models.ForeignKey(Option)
    
    # For GOTO and INPUT (optional)
    IDX = 'idx'   
    # For RECORD
    MAXLENGTH = 'maxlength'
    ONCANCEL = 'oncancel'
    MFID = 'mfid'
    CONFIRM_REC = 'confirm'
    # For TRANSFER
    NUM = 'num'
    # For INPUT (optional)
    NAME = 'name'
    
    name = models.CharField(max_length=24)
    
    value = models.CharField(max_length=128)
    
class Input(models.Model):
    '''
    **********************************************************
    'call' used to be nullable to allow for inbound calls;
    now that inbound calls also get call objects, the 
    migration made those input objects get -1 for call_id
    '''
    call = models.ForeignKey(Call)
    '''
    **********************************************************
    '''
    prompt = models.ForeignKey(Prompt)
    # empty just in case we just want to record presence
    input = models.CharField(max_length=128, blank=True, null=True)
    