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

from decimal import *
from django.db import models
from django.contrib.auth.models import User as AuthUser
from otalo.surveys.models import Survey, Call
from datetime import datetime
from django.db.models import F

class Line(models.Model):
    number = models.CharField(max_length=24)
    # if the outbound calling number for this number needs to be explicitly
    # set. Useful for toll-free lines which can use a dedicated number in
    # the block other than the pilot to send calls, and then deflect inbound calls
    outbound_number = models.CharField(max_length=24, blank=True, null=True)
    name = models.CharField(max_length=128)
    language = models.CharField(max_length=24)
    # is this line open to any caller or restricted?
    # use in combination with user.allowed
    open = models.BooleanField(default=True)
    # does this line allow missed calls to be called back?
    # use in combination with user.quota (TODO)
    callback = models.BooleanField(default=False)
    # does this line use quotas for free access?
    quota = models.BooleanField(default=False)
    # for dialing out
    dialstring_prefix = models.CharField(max_length=128, blank=True, null=True)
    dialstring_suffix = models.CharField(max_length=128, blank=True, null=True)
    # for personal inbox in the main menu
    personalinbox = models.BooleanField(default=True)
    checkpendingmsgs = models.BooleanField(default=True)
    name_file = models.CharField(max_length=24, blank=True, null=True)
    logo_file = models.CharField(max_length=24, blank=True, null=True)
    forums = models.ManyToManyField('Forum', blank=True, null=True)
    sms_config = models.ForeignKey('sms.Config', blank=True, null=True)
    bcasting_allowed = models.BooleanField(default=True)
    
    '''
        max_call_block and min_interval_mins are used to restrict how much broadcasting
        this line can do. Useful when you are sharing a physical phone line amongst many
        line applications
    '''
    # max number of calls you can make simultaneously
    max_call_block = models.IntegerField(blank=True, null=True)
    # minimum period between blocks of calls
    min_interval_mins = models.IntegerField(blank=True, null=True)
    
    def __unicode__(self):
        return self.name + '-' + self.number

class User(models.Model):
    number = models.CharField(max_length=24)
    allowed = models.CharField(max_length=1)
    name = models.CharField(max_length=128, blank=True, null=True)
    district = models.CharField(max_length=128, blank=True, null=True)
    taluka = models.CharField(max_length=128, blank=True, null=True)
    village = models.CharField(max_length=128, blank=True, null=True)
    name_file = models.CharField(max_length=24, blank=True, null=True)
    district_file = models.CharField(max_length=24, blank=True, null=True)
    taluka_file = models.CharField(max_length=24, blank=True, null=True)
    village_file = models.CharField(max_length=24, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    balance_last_updated = models.DateTimeField(blank=True, null=True)
    email = models.CharField(max_length=64, blank=True, null=True)
    # whether broadcasts should consider this number if found
    # from indirect sources (log, based on tags, etc.)
    indirect_bcasts_allowed = models.BooleanField(default=True)
    tags = models.ManyToManyField('Tag', blank=True, null=True)

    def __unicode__(self):
        if self.name and self.name != '':
            return self.name
        else:
            return self.number
        
class Message(models.Model):
    date = models.DateTimeField()
    content_file = models.CharField(max_length=48)
    summary_file = models.CharField(max_length=48, blank=True, null=True)
    user = models.ForeignKey(User)    
    thread = models.ForeignKey('self', blank=True, null=True)
    lft = models.IntegerField(default=1) 
    rgt = models.IntegerField(default=2)
    # Leave out many_to_many with responder since it has two foreign keys into User
    
    def __unicode__(self):
        return datetime.strftime(self.date, '%b-%d-%Y') + '_' + unicode(self.user)
      
class Forum(models.Model):
    name = models.CharField(max_length=128)
    name_file = models.CharField(max_length=24, blank=True, null=True)
    moderated = models.CharField(max_length=1)
    posting_allowed = models.CharField(max_length=1)
    responses_allowed = models.CharField(max_length=1)
    #===========================================================
    # To determine whether a moderated forum suggests
    # responders to route top-level posts to upon approval
    routeable = models.CharField(max_length=1)
    #===========================================================
    # purely for the phone interface. If this false, then 
    listening_allowed = models.BooleanField(default=True)
    
    '''
    ' On approved responses, should a response call be automatically
    ' be scheduled to the original poster?
    '''
    response_calls = models.BooleanField(default=True)
    # On answer calls that go out, do you want to prompt for a response
    # to the response that was played
    respondtoresponse_allowed = models.BooleanField(default=False)
    # The coded value specified for the object must be consistent with paths.lua
    FILTER_CODE_ALL_ONLY = 0
    FILTER_CODE_ALL_FIRST = 1
    FILTER_CODE_NO_ALL = 2
    FILTER_CODE_ALL_LAST = 3
    filter_code = models.IntegerField(default=0)
     ########################################################################################
    # why? so that experts can be associated with not only a topic
    # but also a community (i.e. forum) where they should share that expertise
    # Put another way, a cotton expert in Guj may not want or be qualified to
    # answer cotton questions from a forum for MP farmers.
    # This also makes it so forums develop a specific vocabulary for people to be experts in
    tags = models.ManyToManyField('Tag', through='Forum_tag', blank=True, null=True)
    responders = models.ManyToManyField(User, blank=True, null=True)
    ########################################################################################
    
    maxlength = models.IntegerField()
    max_responder_len = models.IntegerField(blank=True, null=True)
    MAX_RESPONDER_LEN_DEF = 300
    max_user_resp_len = models.IntegerField(blank=True, null=True)
    MAX_USER_RESP_LEN_DEF = 60
    
    messages = models.ManyToManyField(Message, through="Message_forum", blank=True, null=True)
    bcast_template = models.ForeignKey(Survey, blank=True, null=True)
    confirm_recordings = models.BooleanField(default=True)
    # How messages from this forum can be user-forwarded
    # On inbound calls, outbound calls, both, or neither?
    NO_FORWARD = 0
    FORWARD = 1
    FORWARD_INBOUND_ONLY = 2
    FORWARD_OUTBOUND_ONLY = 3
    
    FORWARD_TYPES = (
    (NO_FORWARD, 'No forwarding'),
    (FORWARD, 'All forwarding'),
    (FORWARD_OUTBOUND_ONLY, 'Forwarding from inbound only'),
    (FORWARD_OUTBOUND_ONLY, 'Forwarding from outbound only'),
    )
    forwarding = models.IntegerField(choices=FORWARD_TYPES, blank=True, null=True)
    
    '''
    '########################################################################################
    ' Begin group-related additions
    '''
    STATUS_BCAST_CALL_SMS = 1
    STATUS_BCAST_SMS = 2
    STATUS_INACTIVE = 3
    STATUS_BCAST_CALL = 4
    status = models.IntegerField(blank=True, null=True)
    # The display name of the owner of this group
    sendername = models.CharField(max_length=128, blank=True, null=True)
    members = models.ManyToManyField(User, through='Membership', related_name='members', blank=True, null=True)
    add_member_credits = models.IntegerField(blank=True, null=True)
    backup_calls = models.IntegerField(blank=True, null=True)
    
    '''
    '    Adapted fields (to avoid creating extra fields)
    '    ----------------------------------------------
    '    responses_allowed => response_type (voice = True, touchtone = False)
    '    max_responder_len => maximum input length for touchtone input
    '''
    
    '''
    ' End group-related additions
    '########################################################################################
    '''
    
    def __unicode__(self):
        return self.name
    
class Tag(models.Model):
    tag = models.CharField(max_length=256)
    type = models.CharField(max_length=24, blank=True, null=True)
    tag_file = models.CharField(max_length=24, blank=True, null=True)
    
    def __unicode__(self):
        return self.tag
    
class Forum_tag(models.Model):
    forum = models.ForeignKey(Forum)
    tag = models.ForeignKey(Tag)
    filtering_allowed = models.BooleanField(default=False)
    
    def __unicode__(self):
        return unicode(self.forum) + '_' + unicode(self.tag)
 
class Message_forum(models.Model):
    message = models.ForeignKey(Message)
    forum = models.ForeignKey(Forum)
    
    # Code in order of how they are declared in Message.java
    STATUS_PENDING = 0
    STATUS_APPROVED = 1
    STATUS_REJECTED = 2
    
    STATUSES = (
    (STATUS_PENDING, 'Pending'),
    (STATUS_APPROVED, 'Approved'),
    (STATUS_REJECTED, 'Rejected'),
    )
    
    status = models.IntegerField()
    
    position = models.IntegerField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, null=True)
    
    def __unicode__(self):
        return unicode(self.message) + '_' + unicode(self.forum) + '_(' + str(self.id) + ')'
    
class Message_responder(models.Model):
    # need forum so that you can retrieve responders
    # for a message by the specific forum
    message_forum = models.ForeignKey(Message_forum)
    user = models.ForeignKey(User)
    assign_date = models.DateTimeField()
    listens = models.IntegerField(default=0)
    reserved_by = models.ForeignKey(User, related_name='reserved_by', blank=True, null=True)
    reserved_until = models.DateTimeField(blank=True, null=True)
    passed_date = models.DateTimeField(blank=True, null=True)
    
    def __unicode__(self):
        return unicode(self.message_forum) + '_' + unicode(self.user)

class Admin(models.Model):
    user = models.ForeignKey(User)
    forum = models.ForeignKey(Forum)
    auth_user = models.ForeignKey(AuthUser)
    
    def __unicode__(self):
        return unicode(self.user) + '_' + unicode(self.forum)
    
class Membership(models.Model):
    '''
        UNCONFIRMED is when a member is added by owner but member
        has not taken an action
        SUSCRIBED and UNSUCBSCRIBED are actions taken by the member
        If an unconfirmed member subscribes, they are automatically
        SUBSCRIBED.
        If an unsubscribed member subscribes, they are automatically
        SUBSCRIBED.
        If totally new member subscribes, they are REQUESTED.
        DELETED is an action taken by the group owner. If the member
        is DELETED and subscribes, they are REQUESTED. 
    '''
    STATUS_SUBSCRIBED = 0
    STATUS_UNSUBSCRIBED = 1
    STATUS_REQUESTED = 2
    STATUS_INVITED = 3
    STATUS_DELETED = 4
    STATUS_DNC = 5
    
    STATUS = (
    (STATUS_SUBSCRIBED, 'Joined'),
    (STATUS_UNSUBSCRIBED, 'Unsubscribed'),
    (STATUS_REQUESTED, 'Requested'),
    (STATUS_INVITED, 'Pending'),
    (STATUS_DELETED, 'Deleted'),
    (STATUS_DNC, 'Do not call'),
    )

    user = models.ForeignKey(User)
    group = models.ForeignKey(Forum)
    status = models.IntegerField(choices=STATUS)
    '''
    ****************************************************************************************************
    '''
    '''
    This is the member's display name that is associated with this group.
    It is set and updated by the person(s) who have access to this group's
    membership. When the name is added and.or changed by them, this value is updated only.
    
    This is to account for these cases:
        1) A group owner adds a number with the name different or misspelled from what's in the system
        2) multiple group owners add a number and name the person differently (or
            one person has the name and the other doesn't)
        3) The actual user creates their own account and sets their name (which should not change)
    '''
    membername = models.CharField(max_length=128, blank=True, null=True)
    '''
    ****************************************************************************************************
    '''
    
    added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return unicode(self.user) + '_' + unicode(self.group) +"-" + unicode(self.status)

class Transaction(models.Model):
    BROADCAST_CALL = 0
    INBOUND_CALL = 1
    RECHARGE = 2
    SMS = 3
    TRANSFER_OUT = 4
    TRANSFER_IN = 5
    
    TYPE = (
    (BROADCAST_CALL, 'Broadcast'),
    (INBOUND_CALL, 'Inbound Call'),
    (RECHARGE, 'Recharge'),
    (SMS, 'SMS'),
    (TRANSFER_OUT, 'Transfer out'),
    (TRANSFER_IN, 'Transfer in'),
    )
    
    user = models.ForeignKey(User)
    type = models.IntegerField(choices=TYPE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    
    '''
    ' In order to link transactions back to specific calls
    ' (this is only for auditing purposes; assuming the software works
    '    as supposed to, each call should have an xact associated with it
    '    
    ' Make nullable in order to account for non-call related xacts (like recharge)
    '''
    call = models.ForeignKey(Call, blank=True, null=True)
        
    def __unicode__(self):
        return unicode(self.user) + '_' + unicode(self.type) +"-"+ unicode(self.call) + "-" + unicode(self.amount)

class Forward(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    requestor = models.ForeignKey(User)
    message = models.ForeignKey(Message)
    survey = models.ForeignKey(Survey, blank=True, null=True)
    forum = models.ForeignKey(Forum, blank=True, null=True)
    recipients = models.ManyToManyField(User, related_name='recipients', blank=True, null=True)
        
    def __unicode__(self):
        return unicode(self.requestor) + '_' + datetime.strftime(self.created_on, '%b-%d-%Y')
    
#class DoNotCall(models.Model):
#    user = models.ForeignKey(User)
#    call = models.BooleanField()
#    # Categorical SMS
#    banking = models.NullBooleanField()
#    realestate = models.NullBooleanField()
#    education = models.NullBooleanField()
#    health = models.NullBooleanField()
#    consumergoods = models.NullBooleanField()
#    tourism = models.NullBooleanField()
#    communication = models.NullBooleanField(