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
    
    '''
    '    Next-gen outbound dialing support
    '    Decouples a number (which is essentially what a line models)
    '    from dialing resources, so you can connect a number to multiple
    '    dialing resources, and a dialing resource to many numbers
    ''' 
    dialers = models.ManyToManyField('Dialer', blank=True, null=True)
    
    # for personal inbox in the main menu
    personalinbox = models.BooleanField(default=True)
    checkpendingmsgs = models.BooleanField(default=True)
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
    file = models.FileField(upload_to="%Y/%m/%d")
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
    
    def get_language(self):
        line = self.line_set.all()[0]
        return line.language
    
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
    tag_file = models.CharField(max_length=24, blank=True, null=True)
    
    def __unicode__(self):
        return self.tag
    
class Forum_tag(models.Model):
    forum = models.ForeignKey(Forum)
    tag = models.ForeignKey(Tag)
    filtering_allowed = models.BooleanField(default=False)
    filter_order = models.IntegerField(blank=True, null=True)
    
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
    
    #Used for search index updating
    last_updated = models.DateTimeField(auto_now=True)
    
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
    (STATUS_SUBSCRIBED, 'Subscribed'),
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
    FORWARD = 6
    PAYMENT_GATEWAY_RECHARGE = 7
    
    TYPE = (
    (BROADCAST_CALL, 'Broadcast'),
    (INBOUND_CALL, 'Inbound Call'),
    (RECHARGE, 'Recharge'),
    (SMS, 'SMS'),
    (TRANSFER_OUT, 'Transfer out'),
    (TRANSFER_IN, 'Transfer in'),
    (FORWARD, 'Forward'),
    (PAYMENT_GATEWAY_RECHARGE, 'Payment Gateway Recharge'),
    )
    
    
    '''
    Status - this is for payment gateway/third party payment
    '''
    PAYMENT_STATUS_SUCCESSFUL = 0
    PAYMENT_STATUS_FAILED     = 1
    PAYMENT_STATUS_HOLD       = 2
    PAYMENT_STATUS_INITIATED = 3
    PAYMENT_STATUS_CANCELLED  = 4
    
    PAYMENT_STATUS = (
    (PAYMENT_STATUS_SUCCESSFUL, 'Transaction Successful'),
    (PAYMENT_STATUS_FAILED, 'Transaction Failed'),
    (PAYMENT_STATUS_INITIATED, 'Transaction Initiated'),
    (PAYMENT_STATUS_HOLD, 'Transaction was successful but its still processing recharge'),
    (PAYMENT_STATUS_CANCELLED, 'User cancelled transaction'),
    )
    
    
    user = models.ForeignKey(User)
    type = models.IntegerField(choices=TYPE)
    amount = models.DecimalField(max_digits=10, decimal_places=2) #this is storing no. of credits
    date = models.DateTimeField(auto_now_add=True)
    
    currency_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) # this is actual amount paid in Rs.
    
    #Third party(payment gateway) related fields
    order_ref_no = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    thirdparty_transaction_id = models.CharField(max_length=20, blank=True, null=True)
    thirdparty_name = models.CharField(max_length=12, blank=True, null=True)
    payment_status = models.IntegerField(choices=PAYMENT_STATUS, default=PAYMENT_STATUS_INITIATED, blank=True, null=True)
    
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

'''
'    Represents a forward request from a requestor to some number
'    of recipients. Doesn't give any information on the actual calls
'    (that should be done through Surveys)
'''
class Forward(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    requestor = models.ForeignKey(User)
    message = models.ForeignKey(Message)
    '''
    '    This is the survey the forward was made *from*,
    '    not the survey that was created as a result of this fwd request
    '''
    survey = models.ForeignKey(Survey, blank=True, null=True)
    forum = models.ForeignKey(Forum, blank=True, null=True)
    recipients = models.ManyToManyField(User, related_name='recipients', blank=True, null=True)
        
    def __unicode__(self):
        return unicode(self.requestor) + '_' + datetime.strftime(self.created_on, '%b-%d-%Y %H:%M')
    
'''
'    A dialer is an outbound calling resource.
'    Could be PRI, GSM SIM, VoIP connection, etc.
'    Modeled as a PRI line, which has a series
'    of consecutive phone numbers and can make a set number
'    of parallel calls
'''
class Dialer(models.Model):
    TYPE_PRI = 0
    TYPE_VOIP = 1
    
    TYPES = (
    (TYPE_PRI, 'PRI'),
    (TYPE_VOIP, 'VoIP'),
    )
    
    base_number = models.CharField(max_length=24)
    max_nums = models.IntegerField()
    type = models.IntegerField(choices=TYPES)
    
    '''
    '****************************************************************************************************
    '    Set up dialers to allow for varying levels of inbound (missed call) and outbound traffic.
    '    In a scenario where one line has multiple dialers (or one dialer has multiple lines), 
    '    you can allocate some of the dialers (or parts of dialers) for inbound, and some for broadcasting.
    '
    '    Pure inbound lines (i.e. no missed call) does not need max_parallel_in, since the call
    '    will simply find an available channel automatically if there is one, be go busy if not.
    '
    '    In the case of missed call lines, the inbound call will use the max_parallel_in value to determine
    '    the capacity of the dialer. Since these calls are not scheduled and thus simply look for a spare channel, 
    '    the max_in number should specify *total* inbound capacity, not the number of total channels minus the max_outbound. 
    '    So the max_in and max_out need not add up to the total number of available channels.
    '
    '    Making max_in lower than full capacity can be done to direct missed call traffic toward
    '    some dialers and not others (in the case, for e.g., that a dialer is dedicated for outbound bcasts and
    '    it is under heavy load. In that case you don't even want a missed call to sneak in since there is a
    '    batch of bcast calls to be scheduled that need all the channels).
    '
    '    In the case of a VoIP line, both in and out capacity can be set to very high, since there is no
    '    restriction as with PRIs to limit to a certain number of channels.
    '''
    # How many inbound calls can this dialer allow at one time?
    max_parallel_in = models.IntegerField(blank=True, null=True)
    # How many broadcast calls can this dialer make at one time?
    max_parallel_out = models.IntegerField(blank=True, null=True)
    '''
    ****************************************************************************************************
    '''
    
    # How far apart should calls be spread out
    # between bursts? Depends on the expected
    # length of calls
    interval_mins = models.IntegerField(blank=True, null=True)
    # Should be set to how often your broadcaster cron runs
    MIN_INTERVAL_MINS = 3
    
    dialstring_prefix = models.CharField(max_length=128, blank=True, null=True)
    dialstring_suffix = models.CharField(max_length=128, blank=True, null=True)
    
    '''
    '****************************************************************************************************
    '    Support for variable length dialing. Need this for phone numbers of varying lengths. Before
    '    we were simply capturing the last 10 digits of incoming caller. But what if the number is longer?
    '    To properly capture varying length numbers, need to pattern match out the preamble (country_code)
    '    and capture the remainder as a variable length phone number.
    '    
    '    contry_code => preamble for the base phone number. Usually country_code in international dialing case
    '
    '    min_number_len => minimum number of digits in a valid phone number. Don't need to specify
    '                        max since the pattern matcher will just capture all digits following
    '                        the minimum using %d*
    '    
    '''
    country_code = models.CharField(max_length=24, blank=True, null=True)
    min_number_len = models.IntegerField(blank=True, null=True)
    '''
    ****************************************************************************************************
    '''
    
    '''
    '****************************************************************************************************
    '    Support for multi-tenancy telephony servers. Before this field was added, we assumed a single
    '    telephony server would be making all outbound calls. So when a dialer created a call with prefix
    '    freetdm/grp3/a/XXX, there was no ambiguity about the PRI line that is to make the call.
    '    But if multiple servers are hooked up to the db, both may have grp3 and so both may try to make the
    '    call. To address this we can identify machines by their machine_id. MACHINE_ID is set on the machine
    '    in survey.lua, so your dialer's ID must correspond.
    '    
    '    We could model machines in the DB, but it doesn't seem necessary at this point since all we need
    '    to do is differentiate machines from each other
    '
    '    Now there are three redundant fields between dialers and calls: dialstring_prefix, suffix, and machine_id
    '    Could consider passing a dialer as a foreign key to Call, but that would mean an extra db lookup on each call
    '    in survey.lua. So cache it for now, if the fields pile up further we can make a change.
    '
    '    In most setups, multi-tenant telephony servers won't be needed, so make this a nullable field
    '''
    machine_id = models.IntegerField(blank=True, null=True)
    '''
    ****************************************************************************************************
    '''
    
    '''
    '    If this dialer has any specific channel variables to be set for outbound calls,
    '    define them here in a comma-seperated string with no spaces. 
    '    Can also support wildcards that correspond to variables in
    '    the IVR apps. Currently supported wildcards:
    '
    '    __destination__ => otalo.lua:destination
    '
    '    Example channel_var values:
    '    'sip_from_uri=__destination__@1.2.3.4,sip_h_P-Preferred-Identity=sip:1234567890@1.2.3.4'
    '''
    channel_vars = models.CharField(max_length=200, blank=True, null=True)
    
    def __unicode__(self):
        if self.country_code:
            return unicode(self.base_number) + '_' + unicode(self.dialstring_prefix) + '_' + unicode(self.country_code)
        else:
            return unicode(self.base_number) + '_' + unicode(self.dialstring_prefix)