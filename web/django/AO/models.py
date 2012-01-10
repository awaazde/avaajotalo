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
from django.contrib.auth.models import User as AuthUser
from otalo.surveys.models import Survey
from datetime import datetime

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
    name_file = models.CharField(max_length=24, blank=True, null=True)
    logo_file = models.CharField(max_length=24, blank=True, null=True)
    forums = models.ManyToManyField('Forum', blank=True, null=True)
    
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
    balance = models.IntegerField(blank=True, null=True)
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
    name = models.CharField(max_length=24)
    name_file = models.CharField(max_length=24)
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

    def __unicode__(self):
        return self.name
    
class Tag(models.Model):
    tag = models.CharField(max_length=48)
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

    