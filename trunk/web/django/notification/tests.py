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

"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from otalo.AO.models import User, Tag
from otalo.notification.models import Notification
from otalo.notification.notification_utils import *
import notifications

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}
testUser = User.objects.get(pk=2)

class SMSTest(TestCase):
    notif = Notification.objects.get(action_function__icontains='SMS')
    tag = Tag.objects.get(pk=1)
    notification_utils.action_detailed_sms_to_user(test_user, notif, tag)
    
    notifications.deliver_notifications()
    
class VoiceNotifTest(TestCase):
    notif = Notification.objects.get(action_function__icontains='voice')
    tag = Tag.objects.get(pk=1)
    notification_utils.action_voice_call(test_user, notif, tag)
    
    notifications.deliver_notifications()
