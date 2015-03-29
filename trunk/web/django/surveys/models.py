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
from django.db.models import Q
from django.contrib.admin.util import NestedObjects
from django.db.models.fields.related import ForeignKey
from datetime import datetime

class Subject(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)
    number = models.CharField(max_length=24)
    group = models.IntegerField(blank=True, null=True)
    
    def __unicode__(self):
        if self.name:
            return self.name + '-' + self.number
        else:
            return self.number
    
class Survey(models.Model):
    name = models.CharField(max_length=128)
    complete_after = models.IntegerField(blank=True, null=True)
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
    
    # For delayed broadcasts
    # (when a scheduler needs to schedule calls for a bcast at a later date from when it's created)
    # Don't make auto in order to keep null where not needed and to allow manual setting in test suites
    created_on = models.DateTimeField(blank=True, null=True)
    
    '''
    '    ISFORWARD (added 'is' to avoid reverse query clash with ao.Forward)
    '
    '    Could have used a designator in survey name, or could have simply inferred
    '    from setting template and broadcast to False. Chose to do this because
    '    adding an additional Boolean column doesn't cost a huge performance hit,
    '    makes code more readable and understandable if you can declare a survey
    '    as a forward (instead of inferring based on what it is not).
    '    
    '    Make nullable for backwards-compatibility... don't need to update all old
    '    surveys; since this is a new feature, future forwards should just declare
    '    themselves as such.
    '
    '    With all of these boolean designators, a rewrite may include consolidating
    '    them all into a 'properties' bitmap field
    '''
    isforward = models.NullBooleanField()
    
    '''
    '     For inbound surveys' callback with spoofed numbers (e.g. for VoIP calling)
    '''
    outbound_number = models.CharField(max_length=24, blank=True, null=True)
    
    '''
    '############################################################################
    '    For dynamic scheduling support
    '''
    subjects = models.ManyToManyField(Subject, blank=True, null=True)
    backup_calls = models.IntegerField(blank=True, null=True)
    '''
    '    Next-gen outbound dialing support
    '    Associating a survey with a registered dialer(s)
    '    let's an inbound survey have dialing resources to do
    '    call back on a missed call. Since we schedule outbound
    '    broadcasts by finding surveys from dialers themselves,
    '    this collection isn't useful for outbound calling
    ''' 
    dialers = models.ManyToManyField('ao.Dialer', blank=True, null=True)
    '''
    '############################################################################
    '''
    
    '''
    A way to trace SMS messages sent on behalf of a survey (usually a broadcast)
    This is important for making sure that asynchrous brodcasts can account for
    all SMS sent, for example, in order to limit to one per recipient.
    
    This field will store comma-separated SMSids. Can't use OneToManyField because
    Django currently doesn't support one. Can't use foreign key on SMSMessage because
    that model is a utility and should not be associated with app-specific objects whereever
    possible (even User should eventually be Django User).
    
    Use a text field to support variable number of potentially large-digit SMSids
    '''
    sms_ids = models.TextField(blank=True, null=True)
    
    def getstatus(self):
        now = datetime.now()
        
        if self.subjects.all():
            backup_calls = self.backup_calls or 0
            complete_cnt = self.subjects.filter(Q(call__complete=True) | Q(call__priority=(self.backup_calls or 0)+1), call__survey=self).distinct().count()
            pendingcallcnt = self.subjects.all().count() - complete_cnt
        else:
            # for legacy (pre-survey.subjects) purposes
            pendingcallcnt = Call.objects.filter(survey=self, date__gt=now).count()
            
        if pendingcallcnt == 0 and not self.status == Survey.STATUS_CANCELLED:
            self.status = Survey.STATUS_EXPIRED
            self.save()
        
        return self.status
    
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
        collector = NestedObjects(using='default')
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
        
    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return str(self.id)
    
class Call(models.Model):
    subject = models.ForeignKey(Subject)
    survey = models.ForeignKey(Survey)
    date = models.DateTimeField()
    # Don't set priority for inbound calls. If you do, then the
    # below integrity constraint will be violoated.
    # Note that only MySQL follows this spec. If we
    # use another db, you may get data integrity errors
    # see http://stackoverflow.com/questions/3712222/does-mysql-ignore-null-values-on-unique-constraints
    priority = models.IntegerField(blank=True, null=True)
    complete = models.NullBooleanField(default=False)
    
    duration = models.IntegerField(blank=True, null=True)
    
    '''
    '    The actual selected dialing resource this call should use, set at schedule time.
    '    The survey has all possible dialers; this is the dialer that was actually chosen
    '    given line availability.
    '
    '    Nullable because we don't set this with inbound (missed calls)
    '''
    dialer = models.ForeignKey('ao.Dialer', blank=True, null=True)
    
    '''
    '    Report the hangup cause. If the call didn't connect at all (i.e. on an outbound call), report
    '    the failure cause.
    '
    '    Making it a charfield because that's how they come straight from IVR stack
    '''  
    hangup_cause = models.CharField(max_length=128, blank=True, null=True) 
    # make sure max_retries is at least as big as number of backup calls, or else the limit
    # won't be applied
    HANGUP_CAUSES = {
                     "UNSPECIFIED" : {"code": 0, "report_desc" : "unspecified exchange error"},
                     "UNALLOCATED_NUMBER" : {"code": 1},
                     "NO_ROUTE_DESTINATION" : {"code": 3},
                     "CHANNEL_UNACCEPTABLE" : {"code": 6},
                     "NORMAL_CLEARING" : {"code": 16},
                     "USER_BUSY" : {"code": 17},
                     "NO_USER_RESPONSE" : {"code": 18},
                     "NO_ANSWER" : {"code": 19},
                     "CALL_REJECTED" : {"code": 21},
                     "DESTINATION_OUT_OF_ORDER" : {"code": 27},
                     "INVALID_NUMBER_FORMAT" : {"code": 28},
                     "NORMAL_UNSPECIFIED" : {"code": 31},
                     "NORMAL_CIRCUIT_CONGESTION" : {"code": 34, "max_retries" : 5},
                     "NETWORK_OUT_OF_ORDER" : {"code": 38},
                     "NORMAL_TEMPORARY_FAILURE" : {"code": 41, "max_retries" : 5},
                     "REQUESTED_CHAN_UNAVAIL" : {"code": 44},
                     "WRONG_CALL_STATE" : {"code": 101},
                     "RECOVERY_ON_TIMER_EXPIRE" : {"code": 102},
                     "PROTOCOL_ERROR" : {"code": 111},
                     "INTERWORKING" : {"code": 127},
                     "ORIGINATOR_CANCEL" : {"code": 487},
                     
                     ''' App-defined codes. Must be consistent with paths.lua '''
                     "APP_HANGUP" : {},
                     "CALLER_HANGUP" : {},
                     "NO_RESP_HANGUP" : {},
                     } 
    
    HUP_CAUSES_WITH_LIMIT = {k:v['max_retries'] for (k,v) in HANGUP_CAUSES.iteritems() if 'max_retries' in v}
     
    class Meta:
        '''  Add a unique key constraint to prevent asynchronous task scheduling from 
        '    adding extra objects due to race conditions on creation of a Call object
        '    by multiple workers. E.g.:
        '
        '    1. scheduler schedules a task t1 to queue q1 for subj/survey/pri combo c1
        '    2. t1 is enqueued, but does not execute
        '    3. schedule schedules a task t2 to queue q2 for same c1 combo
        '    4. t1 executes and creates call object for c1
        '    5. t2 executes and creates call object for c1 in a race
        '''
        unique_together = ('subject', 'survey', 'priority')
    
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
    # the prompt has sub-prompts to be played in random order
    random = models.NullBooleanField() 
    
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
    FORWARD = 8
    
    action = models.IntegerField()
    
    prompt = models.ForeignKey(Prompt)
    
    def __unicode__(self):
        if self.number == '':
            return 'noinput-' + str(self.action)
        else:
            return self.number + '-' + str(self.action)
    
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
    # For FORWARD
    FWD_PROMPT_PATH = 'fwdpath'
        
    name = models.CharField(max_length=24)
    
    value = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.name + '-' + self.value
    
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
    