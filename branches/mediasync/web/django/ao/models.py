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

import random, string
from decimal import *
from django.db import models
from django.contrib.auth.models import User as AuthUser
from otalo.surveys.models import Survey, Call
from datetime import datetime
from django.db.models import F
from django.utils.translation import ugettext_lazy as _

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
    no_login = models.IntegerField(blank=True, null=True) #keeping track of logins
    
    # a secret amount of money that signals
    # that this is account has unlimited credits. Choose an amount
    # that can't actually be reached through any
    # combo of transactions
    UNLIMITED_BALANCE = 999
    # Disallow bcasting if balance below this amount
    BCAST_DISALLOW_BALANCE_THRESH = 0
    balance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    balance_last_updated = models.DateTimeField(blank=True, null=True)
    
    email = models.CharField(max_length=64, blank=True, null=True)
    # whether broadcasts should consider this number if found
    # from indirect sources (log, based on tags, etc.)
    indirect_bcasts_allowed = models.BooleanField(default=True)
    tags = models.ManyToManyField('Tag', blank=True, null=True)
    
    ''' number of groups this user (i.e. account) can create
        This will become a user setting value in 2.0 architecture
    '''
    DISABLE_GROUP_ADD_REMOVE = -1;
    max_groups = models.IntegerField(blank=True, null=True)

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
    '''
    # y if messages need to be approved or rejected, n if they should be approved by default
    # In the console, setting this to y will result in an Inbox, Approved, and Rejected
    # folders to appear, with new messages being status PENDING by default. If set to n,
    # There will only be an Approved folder
    '''
    moderated = models.CharField(max_length=1)
    ''' y if this forum has the option to record a new message (i.e. new thread), n if not '''
    posting_allowed = models.CharField(max_length=1)
    ''' y if callers to this forum can record a response to an existing message, n if not '''
    responses_allowed = models.CharField(max_length=1)
    '''
    #===========================================================
    # To determine whether a moderated forum suggests
    # responders to route top-level posts to upon approval
    # i.e., is there a listbox with responders listed to assign a message to?
    '''
    routeable = models.CharField(max_length=1)
    '''
    #===========================================================
    # True if this forum has the option to listen to (approved) messages, n if not
    '''
    listening_allowed = models.BooleanField(default=True)
    
    '''
    ' On approved responses, should a response call be automatically
    ' be scheduled to the original poster?
    '''
    response_calls = models.BooleanField(default=True)
    '''
    # On answer calls that go out, do you want to prompt for a response
    # to the response that was played
    '''
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
    ''' maximum length in seconds of a responder's message '''
    max_responder_len = models.IntegerField(blank=True, null=True)
    MAX_RESPONDER_LEN_DEF = 300
    ''' maximum length in seconds of a caller to the forum's response to another caller's message '''
    max_user_resp_len = models.IntegerField(blank=True, null=True)
    MAX_USER_RESP_LEN_DEF = 60
    
    messages = models.ManyToManyField(Message, through="Message_forum", blank=True, null=True)
    bcast_template = models.ForeignKey(Survey, blank=True, null=True)
    # True if the IVR system should playback a recorded message and ask to approve/re-record/cancel it before
    # saving, False if the first recording should be automatically saved
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
    valid_till field holds the date till this groups is valid. Once reach to this date, the group would be considered as expired once. In case of None, we are assumuing that the group is not purchased by user.
    It's value is set with the date using following way:
    1. Whenever user purchased any group/s, we are creating corresponding PurchaseOrder object and setting validity date in it.
    2. So now when user actually creates a group, we are finding the purchase order which is having group validity date and haven't been used yet. 
       Here unused means the available groups in purchased order is greater than 0. The purchased order would be the older one.
       e.g. let's say user purchased 2 groups, then we are having purchased order containing no_groups and available_groups field with avlue 2 along with groups_validity date.
       Now when user creates a new group, we are taking this purchase order and checking its available_groups field. Since the purchase order is having 2 availbale_groups, we are taking 
       its groups_validity date and setting it here in this field.
       See create_group method in streamit.py. Also reference logic in payment/utils.Util class.
    '''
    valid_till = models.DateTimeField(_("Groups valid till"), blank=True, null=True)
    
    
    
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
    payment_status = models.IntegerField(choices=PAYMENT_STATUS, blank=True, null=True)
    coupon = models.ForeignKey('Coupon', blank=True, null=True) #stores coupon if applied any
    
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
    Adds coupon reference for the transaction
    ''' 
    def add_coupon(self, coupon):
        self.coupon = coupon
        self.save()
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
    
    description = models.CharField(max_length=128, blank=True, null=True)
    '''
    '    Dialers can support (multiple) ranges of numbers
    '    The two below fields work together to define them.
    '    Both are comma-separated.
    '
    '    NOTE outside code should not reference them directly
    '    and instead use the instance method below to access
    '    a dialer's number range
    '''
    base_numbers = models.CharField(max_length=128)
    series_lengths = models.CharField(max_length=128)
    
    '''
    ' Get all possible numbers associated with this dialer
    '''
    def get_dialer_numbers(self):
        nums = []
        bases = self.base_numbers.split(',')
        ranges = self.series_lengths.split(',')
        for base, l in zip(bases, ranges):
            nums += map(str, range(int(base),int(base)+int(l)))
            
        return nums

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
    machine_id = models.CharField(max_length=24, blank=True, null=True)
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
    
    
    '''
    '    Specify a gap between calls on this dialing resource. Each dialer filters into a queue
    '    for calls to be scheduled. That queue (identified by the machine_id) may collect calls from multiple dialers
    '    or a single dialer. Different dialers (esp PRI vs. VoIP) or groups of dialers will have different gap requirements.
    '
    '    Note that this gap is *in addition* to any natural gap introduced by the worker. I.e the queueing system will take
    '    its own time to send a call to the dialing resource. Additionally, depending on the queue's number of parallel
    '    processes executing tasks, calls may execute with much smaller gaps. This setting affects the gap between the worker executing
    '    one and the next set of tasks, if there are multiple processes accessible to the worker.
    ' 
    '    It is the responsibility of the admin to group dialers into queues so that their gap requirements are met. I.e. if you
    '    have PRI dialers, it's your responsibility to define different queues per PRI and set the concurrency to 1. If you have a bunch
    '    of VoIP dialers, you may be OK to put them into a single queue with concurrent processes and with no gap.
    '''
    DEFAULT_CALL_GAP_SECS = 1
    call_gap_secs = models.IntegerField(blank=True, null=True)
    
    def __unicode__(self):
        if self.description:
            return unicode(self.description)
        elif self.country_code:
            return unicode(self.base_numbers) + '_' + unicode(self.dialstring_prefix) + '_' + unicode(self.country_code)
        else:
            return unicode(self.base_numbers) + '_' + unicode(self.dialstring_prefix)
        

'''
Payment related models - We might need to move it into payment app
'''
class Coupon(models.Model):
    MONETARY = 'monetary'
    PERCENTAGE = 'percentage'
    
    COUPON_TYPES = (
        (MONETARY, 'Money based coupon'),
        (PERCENTAGE, 'Percentage discount'),
    )
    
    CODE_LENGTH = 7
    CODE_CHARS = string.letters+string.digits
    
    value = models.IntegerField(_("Value"), help_text=_("Arbitrary coupon value"))
    code = models.CharField(_("Code"), max_length=30, unique=True, blank=True,
        help_text=_("Leaving this field empty will generate a random code."))
    type = models.CharField(_("Type"), max_length=20, choices=COUPON_TYPES)
    user = models.ForeignKey(AuthUser, verbose_name=_("User"), null=True, blank=True,
        help_text=_("You may specify a user you want to restrict this coupon to."))
    created_on = models.DateTimeField(_("Created On"), auto_now_add=True)
    expires_on = models.DateTimeField(_("Expires On"), blank=True, null=True)

    class Meta:
        ordering = ['created_on']
        verbose_name = _("Coupon")
        verbose_name_plural = _("Coupons")

    def __unicode__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = Coupon.generate_code()
        super(Coupon, self).save(*args, **kwargs)

    @classmethod
    def generate_code(cls):
        return "".join(random.choice(Coupon.CODE_CHARS) for i in xrange(Coupon.CODE_LENGTH))


'''
PurchaseOrder model is holding all the purchase information for any online payment

Each important field and its purpose are descibed below:

1. no_members: holds no.of memeber user purchased. This field is filled when user selects the unlimited plan.
2. members_validity: the date till member(unlimited plan) is valid. The value would be date + 6 or 12 months from the date user purchased
   Please note that whenever any value present into this field, it means user has/wanted to purchased unlimited plan. In case of None, the user selects the other pre defined plan.
3. no_groups: no. of groups user purchased. The value of this would be add into max_groups in user model
4. groups_validity: the date till the groups(that the user purchased) are valid.  The value would be date + 6 or 12 months from the date user purchased.
   Whenever the user purchases the groups, this field would be filled. In case of None, we assume that user hasn't purchase the groups. Only recharged his/her account.
5. available_groups: the initial value would be no_groups.  And whenever user creates a new group, the value in this field would be decreased by "1". See payment/utils.Util
'''
class PurchaseOrder(models.Model):
    no_members = models.IntegerField(_("No. of Members"), blank=True, null=True)
    members_validity = models.DateTimeField(_("Members valid till"), blank=True, null=True)
    no_groups = models.IntegerField(_("No. of Groups"), blank=True, null=True)
    groups_validity = models.DateTimeField(_("Groups valid till"), blank=True, null=True)
    created_on = models.DateTimeField(_("Created at"), auto_now_add=True)
    transaction = models.ForeignKey('Transaction', blank=True, null=True)
    available_groups = models.IntegerField(_("Available Groups"), blank=True, null=True)
    
    
    class Meta:
        ordering = ['created_on']
        verbose_name = _("Purchase Order")
        verbose_name_plural = _("Purchase Orders")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.available_groups = self.no_groups
        super(PurchaseOrder, self).save(*args, **kwargs)
        
    def __unicode__(self):
        return str(self.id) + " == " + str(self.created_on) + " == " + str(self.transaction)

    