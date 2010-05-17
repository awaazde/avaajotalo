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
from django.db.models.signals import post_save

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
    maxlength = models.IntegerField()

    def __unicode__(self):
        return self.name


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

    def __unicode__(self):
        if self.name:
            return self.name + '-' + self.number
        else:
            return self.number

class Message(models.Model):
    date = models.DateTimeField()
    content_file = models.CharField(max_length=48)
    summary_file = models.CharField(max_length=48)
    user = models.ForeignKey(User)    
    thread = models.ForeignKey('self', blank=True, null=True)
    lft = models.IntegerField(default=1) 
    rgt = models.IntegerField(default=2)

    def __unicode__(self):
        return str(self.date) + '_' + unicode(self.user)
 
class Message_forum(models.Model):
    message = models.ForeignKey(Message)
    forum = models.ForeignKey(Forum)
    status = models.IntegerField()
    position = models.IntegerField(blank=True, null=True)
    
    def __unicode__(self):
        return unicode(self.message) + '_' + unicode(self.forum)
    
class Tag(models.Model):
    tag = models.CharField(max_length=24)
    type = models.CharField(max_length=24, blank=True, null=True)
    tag_file = models.CharField(max_length=24, blank=True, null=True)
    ########################################################################################
    # why? so that experts can be associated with not only a topic
    # but also a community (i.e. forum) where they should share that expertise
    # Put another way, a cotton expert in Guj may not want or be qualified to
    # answer cotton questions from a forum for MP farmers.
    # This also makes it so forums develop a specific vocabulary for people to be experts in
    forum = models.ForeignKey(Forum)
    ########################################################################################
    
    def __unicode__(self):
        return self.tag
    
class Message_tag(models.Model):
    # need forum so that you can retrieve tags
    # for a message by the specific forum
    message_forum = models.ForeignKey(Message_forum)
    tag = models.ForeignKey(Tag)
    
    def __unicode__(self):
        return unicode(self.message) + '_' + unicode(self.tag)
    
class Responder_tag(models.Model):
    user = models.ForeignKey(User)
    tag = models.ForeignKey(Tag)
    
    def __unicode__(self):
        return unicode(self.user) + '_' + unicode(self.tag)
    
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
        return unicode(self.message) + '_' + unicode(self.user)

class Line(models.Model):
    number = models.CharField(max_length=24)
    name = models.CharField(max_length=128)
    language = models.CharField(max_length=3)
    # for dialing out. The softswitch may need to identify
    # which port/span/group this line is using
    span = models.CharField(max_length=24, blank=True, null=True)
    name_file = models.CharField(max_length=24, blank=True, null=True)
    
    def __unicode__(self):
        return self.name + '-' + self.number

class Line_forum(models.Model):
    line = models.ForeignKey(Line)
    forum = models.ForeignKey(Forum)
    
    def __unicode__(self):
        return unicode(self.line) + '_' + unicode(self.forum)
    
class Admin(models.Model):
    user = models.ForeignKey(User)
    forum = models.ForeignKey(Forum)
    
    def __unicode__(self):
        return unicode(self.user) + '_' + unicode(self.forum)

class Admin_auth(models.Model):
    user = models.ForeignKey(User)
    auth_user = models.ForeignKey(AuthUser)
    
    def __unicode__(self):
        return unicode(self.user) + '_' + unicode(self.auth_user)

def admin_created_handler(sender, **kwargs):
    # an AO admin has been saved. Create a corresponding web admin
    
    # get the AO_admin instance that was created
    admin = kwargs['instance']
    
    # has this admin already had a web account set up?
    new_auth = (Admin_auth.objects.filter(user=admin.user).count() == 0)
    
    if new_auth:
        auth_user = AuthUser.objects.create_user(admin.user.name, '')
        auth_user.save()
        
        admin_auth = Admin_auth(user=admin.user, auth_user=auth_user)
        admin_auth.save()
    
post_save.connect(admin_created_handler, sender=Admin)
    