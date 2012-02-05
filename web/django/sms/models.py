'''
    Copyright (c) 2009 Regents of the University of California, Stanford University, and others
 
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
 
        http://www.apache.org/licenses/LICENSE-2.0
 
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''
from django.db import models
from otalo.AO.models import User
from datetime import datetime

class Config(models.Model):
    """Contains all SMS adapter info
    """
    HEADER = {'Content-type': 'application/x-www-form-urlencoded'}
    # An SMS API has to have at least these three parameters
    url = models.CharField(max_length=128)
    to_param_name = models.CharField(max_length=24)
    text_param_name = models.CharField(max_length=24)
    date_param_name = models.CharField(max_length=24, blank=True, null=True)
    date_param_format = models.CharField(max_length=24, blank=True, null=True)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    '''
        For incoming messages
    '''
    keyword = models.CharField(max_length=24, blank=True, null=True)
    inbound_number = models.CharField(max_length=24, blank=True, null=True)
    
    def __unicode__(self):
        return "[SMS Config: " + self.url + "]"

class ConfigParam(models.Model):
    """Other parameters that this SMS adapter requires to send in the post
    """
    # URL for the aggregator's API
    name =      models.CharField(max_length=24, blank=True,null=True)
    value =     models.CharField(max_length=128, blank=True,null=True)
    
    config =    models.ForeignKey(Config)
    
    def __unicode__(self):
        return "[ConfigParam: name = " + self.name + " value = " + self.value + "]"
    
class SMSMessage(models.Model):
    """ Individual message
    """
    sender =        models.ForeignKey(User, related_name='smssender')
    recipients =    models.ManyToManyField(User, related_name='smsrecipients')
    # date of creation of this object
    created_on =        models.DateTimeField(auto_now_add=True)
    # date at which the notification was sent(or attempted to be sent)
    sent_on =           models.DateTimeField(default=datetime.now)

    text =      models.CharField(max_length=255, null=True, blank=True)
    
    def __unicode__(self):
        return "[SMS: from " + unicode(self.sender) + " text = " + self.text[:10] + "...]"