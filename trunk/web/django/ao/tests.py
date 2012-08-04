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
from datetime import datetime, timedelta
from awaazde.streamit import streamit
from otalo.ao.models import *
from otalo.surveys.models import *
from otalo.sms.models import Config as SMSConfig, ConfigParam, SMSMessage
from django.contrib.auth.models import User as AuthUser

class StreamitTest(TestCase):
    def setUp(self):
        streamit.PROFILES = {'user/':{'basenum':5002, 'maxnums':2, 'maxparallel':2}, 'user2/':{'basenum':6000, 'maxnums':1, 'maxparallel':2}, 'user3/':{'basenum':7000, 'maxnums':10, 'maxparallel':0}}
        streamit.INTERVAL_MINS = 10
        
        streamit.STREAMIT_FILE_DIR = ''
        streamit.STREAMIT_GROUP_LIST_FILENAME = '/Users/neil/Development/groups_test.xlsx'
        
        streamit.SMS_DEFAULT_CONFIG_FILE='/Users/neil/Development/awaazde/streamit/sms.conf'
        info = streamit.load_sms_config_info()
        config = SMSConfig.objects.filter(url=info['url'])
        
        streamit.SMS_INVITE_TEXT = {"eng": "%s invites you to join the %s group. Call 0%s to subscribe.", "hin": "%s invites you to join the %s group. Call 0%s to subscribe."}
        streamit.SMS_MESSAGE_TEXT = {"eng": "New message from %s (%s)! Call 0%s to listen.", "hin": "New message from %s (%s)! Call 0%s to listen."}

        if bool(config):
            config = config[0]
        else:
            config = SMSConfig.objects.create(url=info['url'], to_param_name=info['to'], text_param_name=info['text'], date_param_name=info['date'], date_param_format=info['dateformat'], country_code=info['countrycode'])
            ConfigParam.objects.create(name='feedid', value=info['params']['feedid'], config=config)
            ConfigParam.objects.create(name='username', value=info['params']['username'], config=config)
            ConfigParam.objects.create(name='password', value=info['params']['password'], config=config)
        
        streamit.SMS_DEFAULT_CONFIG_ID=config.id
        
        Line.objects.create(name="SMS", number="N/A", language="N/A", sms_config=config)
        for f in Membership._meta.fields:
            if f.name == 'last_updated':
                f.auto_now=False
                f.default=datetime.now
        
    def test_create_users(self):
        u1 = streamit.update_user('u1','1001')
        u2 = streamit.update_user('u2','1002')
        self.assertEqual(u1.name, 'u1')
        self.assertEqual(u2.name, 'u2')
        
        g1 = streamit.update_group("g1", u1, 'eng')
        g2 = streamit.update_group("g2", u2, 'eng')
        
        self.assertEqual(Forum.objects.all().count(), 2)
        lines = Line.objects.filter(name__contains=streamit.STREAMIT_LINE_DESIGNATOR)
        self.assertEqual(lines.count(),2)
        line1 = lines.filter(name__contains=u1.name)
        self.assertEqual(line1.count(), 1)
        line2 = lines.filter(name__contains=u2.name)
        self.assertEqual(line2.count(), 1)
        
        self.assertEqual(g1.name_file, str(g1.id)+".wav")
        self.assertEqual(g2.name_file, str(g2.id)+".wav")
        
        line1 = line1[0]
        line2 = line2[0]
        
        self.assertEqual(line1.number, '5002')
        self.assertEqual(line2.number, '5003')
        
        u3 = streamit.update_user('u2', '1003')
        streamit.update_group('g3', u3, 'eng')
        lines = Line.objects.filter(name__contains=streamit.STREAMIT_LINE_DESIGNATOR)
        self.assertEqual(lines.count(),3,"Failed to add a new line with overlapping name")
        line3 = Line.objects.get(forums__admin__user=u3)     
        self.assertEqual(line3.number, '6000')
        
        u4 = streamit.update_user('u4', '1002')
        g4 = streamit.update_group('g4', u4, 'eng')
        self.assertEqual(User.objects.all().count(), 3)
        self.assertEqual(AuthUser.objects.all().count(), 3)
        self.assertEqual(Admin.objects.all().count(), 4)
        
        lines = Line.objects.filter(name__contains=streamit.STREAMIT_LINE_DESIGNATOR)
        forums = Forum.objects.all()
        
        self.assertEqual(forums.count(),4)
        self.assertEqual(lines.count(),4, "Failed to add a new line with overlapping number")
        
        line4 = g4.line_set.all()[0]    
        self.assertEqual(line4.number, '7000')
        # get logins
        #auths = AuthUser.objects.all()
        #self.assertEqual(auths.count(),2)
        
        #auth1 = auths.filter(username=u1.name)
    def test_create_groups(self):
        u1 = streamit.update_user('u1','1001')
        u2 = streamit.update_user('u2','1002')
        self.assertEqual(u1.name, 'u1')
        self.assertEqual(u2.name, 'u2')
        
        g1 = streamit.update_group("g1", u1, 'eng')
        g2 = streamit.update_group("g2", u2, 'eng')
        
        lines = Line.objects.filter(name__contains=streamit.STREAMIT_LINE_DESIGNATOR)
        self.assertEqual(lines.count(),2)
        line1 = lines.filter(name__contains=u1.name)
        self.assertEqual(line1.count(), 1)
        line2 = lines.filter(name__contains=u2.name)
        self.assertEqual(line2.count(), 1)
        
        line1 = line1[0]
        line2 = line2[0]
        self.assertEqual(line1.language, 'eng')
        self.assertEqual(line2.language, 'eng')
        
        self.assertEqual(line1.number, '5002')
        self.assertEqual(line2.number, '5003')
        
        self.assertEqual(line1.forums.all().count(), 1)
        self.assertEqual(g1.line_set.all().count(),1)
        self.assertEqual(g1.name, "g1")
        admin = Admin.objects.get(user=u1)
        self.assertEqual(admin.user, u1)
        self.assertEqual(g1, admin.forum)
        self.assertEqual(admin.auth_user.username, 'u1')
        
        self.assertEqual(line2.forums.all().count(), 1)
        self.assertEqual(g2.line_set.all().count(),1)
        self.assertEqual(g2.name, "g2")
        admin = Admin.objects.get(user=u2)
        self.assertEqual(admin.user, u2)
        self.assertEqual(g2, admin.forum)
        self.assertEqual(admin.auth_user.username, 'u2')
        
        streamit.update_group("g1", u1, 'eng')
        streamit.update_group("g2", u2, 'eng')
        
        # make sure nothing new created
        self.assertEqual(Line.objects.filter(name__contains=streamit.STREAMIT_LINE_DESIGNATOR).count(),2)
        self.assertEqual(Forum.objects.all().count(),2)
        self.assertEqual(Admin.objects.all().count(),2)
        self.assertEqual(AuthUser.objects.all().count(),2)
        
        members=[]
        for i in range(10):
            m = User(number=str(i), allowed='y')
            m.save()
            members.append(m)
        
        streamit.add_members(g1, members, Membership.STATUS_SUBSCRIBED, send_sms=False) 
        self.assertEquals(g1.members.all().count(),10)
        self.assertEqual(SMSMessage.objects.filter(sender=u1).count(), 0)
        d = datetime.now()
        streamit.send_invite_sms(g1, members, d)
        sms = SMSMessage.objects.get(sender=u1, sent_on=d)
        self.assertEqual(sms.recipients.all().count(), 10)
        
        line = Line.objects.get(forums__admin__user=u1)
        smstext = "u1 invites you to join the g1 group. Call 0"+line.number+" to subscribe."
        
        self.assertEqual(smstext, sms.text)
        
        g3 = streamit.update_group("g3", u1, 'hin')
        self.assertEqual(Line.objects.filter(name__contains=streamit.STREAMIT_LINE_DESIGNATOR).count(),3)
        self.assertEqual(Forum.objects.all().count(),3)
        self.assertEqual(Admin.objects.all().count(),3)
        self.assertEqual(AuthUser.objects.all().count(),2)
        
        self.assertEqual(Forum.objects.filter(admin__user=u1, name__in=["g1","g3"]).count(),2)
        self.assertEqual(Line.objects.filter(forums__admin__user=u1).count(),2)
        
        
    def test_update_groups(self):
        # create group with members
        u1 = streamit.update_user('u1','1001')
        
        g1 = streamit.update_group("g1", u1, 'eng')
        g2 = streamit.update_group("g2", u1, 'eng')
        g3 = streamit.update_group("g3", u1, 'eng')
        g4 = streamit.update_group("g4", u1, 'eng')
        self.assertEqual(Forum.objects.filter(admin__user=u1).count(),4)
        
        members=[]
        for i in range(10):
            m = User(number=str(i), allowed='y')
            m.save()
            members.append(m)
            
        streamit.add_members(g1, members)
        streamit.add_members(g2, members)
        streamit.add_members(g3, members)
        streamit.add_members(g4, members)
        m11 = User.objects.create(number='11', allowed='y')
        streamit.add_members(g4, members=[m11], status=Membership.STATUS_SUBSCRIBED, send_sms=False)
        self.assertEqual(Membership.objects.filter(group=g1).count(),10)
        self.assertEqual(Membership.objects.filter(group=g2).count(),10)
        self.assertEqual(Membership.objects.filter(group=g3).count(),10)
        self.assertEqual(Membership.objects.filter(group=g4).count(),11)
        self.assertEqual(Membership.objects.filter(group=g4, status=Membership.STATUS_SUBSCRIBED).count(),1)
        
        # update group and members
        #g1 - 0-9
        #g2 - inactive
        #g3 - 0-2
        #g4 - 0-8, 10-12
        m10 = User.objects.create(number='10', allowed='y')
        m12 = User.objects.create(number='12', allowed='y')
        g3mems = User.objects.filter(number__in=[str(num) for num in range(3,10)+[12]])
        # for g1, do nothing
        # for g2, deactivate
        g2.status = Forum.STATUS_INACTIVE
        g2.save()
        # for g3, remove members 3-10. Add m12 just to test that non-members
        # aren't affected by this method
        streamit.update_members(g3,Membership.STATUS_DELETED, members=g3mems)
        # for g4, add 10 and 12 (11 sh be ignored) and remove 9

        u9 = User.objects.get(number='9')
        streamit.update_members(g4,Membership.STATUS_DELETED, members=[u9])
        streamit.add_members(g4,[m10,m11,m12])
        
        # check active statuses
        g1 = Forum.objects.get(pk=g1.id)
        g2 = Forum.objects.get(pk=g2.id)
        g3 = Forum.objects.get(pk=g3.id)
        g4 = Forum.objects.get(pk=g4.id)
        self.assertEqual(g2.status, Forum.STATUS_INACTIVE)
        self.assertEqual(Forum.objects.filter(admin__user=u1, status=Forum.STATUS_BCAST_CALL_SMS).count(),3)
        # check membership changes
        self.assertEqual(Membership.objects.filter(group=g1, status=Membership.STATUS_INVITED).count(),10)
        self.assertEqual(Membership.objects.filter(group=g3, status=Membership.STATUS_INVITED).count(),3)
        self.assertEqual(Membership.objects.filter(group=g3, status=Membership.STATUS_DELETED).count(),7)
        self.assertEqual(Membership.objects.filter(group=g4, status=Membership.STATUS_INVITED).count(),11)
        self.assertEqual(Membership.objects.filter(group=g4, status=Membership.STATUS_SUBSCRIBED).count(),1)
        self.assertEqual(Membership.objects.filter(group=g4, status=Membership.STATUS_DELETED).count(),1)
        
    def test_sched_bcast(self):
        u1 = streamit.update_user('u1','1001')
        g1 = streamit.update_group('g1', u1, 'eng')
        self.assertEqual(Forum.objects.filter(admin__user=u1).count(),1)   
        
        members = []
        for i in range(11):
            m = User(number=str(i), allowed='y')
            m.save()
            members.append(m)
        streamit.add_members(g1, members, status=Membership.STATUS_SUBSCRIBED)
        
        m11 = User.objects.create(name="m11", number="11")
        streamit.add_members(g1, [m11])
        
        u2 = streamit.update_user('u2','1002')
        g2 = streamit.update_group('g1', u2, 'eng')
        self.assertEqual(Forum.objects.filter(admin__user=u2).count(),1)   
        
        streamit.add_members(g2, members, Membership.STATUS_SUBSCRIBED)
            
        u3 = streamit.update_user('u3','1003')
        g3 = streamit.update_group('g3', u3, 'eng')
        self.assertEqual(Forum.objects.filter(admin__user=u3).count(),1)   
        
        streamit.add_members(g3, members, status=Membership.STATUS_SUBSCRIBED)
        
        now = datetime.now()
        nextyear = now.year+1
        d = datetime(year=nextyear, month=1, day=1, hour=10, minute=40)
        
        m = Message(date=d, content_file='foo.mp3', user=u1)
        m.save()
        mf = Message_forum(message=m, forum=g1, status=Message_forum.STATUS_APPROVED)
        mf.save()
        
        # Rejected, so should not be scheduled
        m2 = Message(date=d, content_file='foo2.mp3', user=u1)
        m2.save()
        mf2 = Message_forum(message=m2, forum=g1, status=Message_forum.STATUS_REJECTED)
        mf2.save()
        
        streamit.create_bcasts(d)
        b1 = Survey.objects.get(name=str(mf))
        self.assertEqual(Prompt.objects.filter(survey=b1, file__contains='chooserecord').count(), 1)
        g1.responses_allowed = 'n'
        g1.save()
        b2 = streamit.create_bcast_survey(mf, d)
        self.assertEqual(Prompt.objects.filter(survey=b2, file__contains='chooserecord').count(), 0)
        # Only approved message's bcasts scheduled
        self.assertEqual(Survey.objects.count(), 2)
        
        streamit.schedule_bcasts(d)
        calls = Call.objects.filter(survey__dialstring_prefix=b1.dialstring_prefix, date=d)
        self.assertEqual(calls.count(), 4)
        
        streamit.schedule_bcasts(d+timedelta(minutes=streamit.INTERVAL_MINS*1))
        calls = Call.objects.filter(survey__dialstring_prefix=b1.dialstring_prefix, date=d+timedelta(minutes=streamit.INTERVAL_MINS*1))
        self.assertEqual(calls.count(), 4)
        
        nextd = datetime(year=nextyear, month=1, day=1, hour=11, minute=0)
        streamit.create_bcasts(nextd)
        streamit.unsubscribe_by_broadcast(nextd)
        streamit.schedule_bcasts(nextd)
        self.assertEqual(nextd, d+timedelta(minutes=streamit.INTERVAL_MINS*2))
        calls = Call.objects.filter(survey__dialstring_prefix=b1.dialstring_prefix, date=d+timedelta(minutes=streamit.INTERVAL_MINS*2))
        self.assertEqual(calls.count(), 4)
        
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.create_bcasts(nextd)
        streamit.unsubscribe_by_broadcast(nextd)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(survey__dialstring_prefix=b2.dialstring_prefix, date=nextd)
        self.assertEqual(calls.count(), 4)
        
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.create_bcasts(nextd)
        streamit.unsubscribe_by_broadcast(nextd)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(survey__dialstring_prefix=b2.dialstring_prefix, date=nextd)
        self.assertEqual(calls.count(), 4)
        
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.create_bcasts(nextd)
        streamit.unsubscribe_by_broadcast(nextd)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(survey__dialstring_prefix=b2.dialstring_prefix, date=nextd)
        self.assertEqual(calls.count(), 2)
        
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(survey__dialstring_prefix=b2.dialstring_prefix, date=nextd+timedelta(minutes=streamit.INTERVAL_MINS))
        self.assertEqual(calls.count(), 0)
        
        m3 = Message(date=nextd, content_file='foo3.mp3', user=u2)
        m3.save()
        mf3 = Message_forum(message=m3, forum=g2, status=Message_forum.STATUS_APPROVED)
        mf3.save()
        b3 = streamit.create_bcast_survey(mf3,nextd)
        streamit.schedule_bcasts(nextd)
        
        calls = Call.objects.filter(date=nextd)
        self.assertEqual(calls.count(), 4)
        
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.create_bcasts(nextd)
        streamit.unsubscribe_by_broadcast(nextd)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(date=nextd)
        self.assertEqual(calls.count(), 4)
        
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.create_bcasts(nextd)
        streamit.unsubscribe_by_broadcast(nextd)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(date=nextd)
        self.assertEqual(calls.count(), 4)
        
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.create_bcasts(nextd)
        streamit.unsubscribe_by_broadcast(nextd)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(date=nextd)
        self.assertEqual(calls.count(), 1)
        
        # add some more members to g2: subscribed and requested
        for i in range(12,16):
            m = User.objects.create(number=str(i), allowed='y')
            streamit.add_members(g2, [m], Membership.STATUS_REQUESTED, send_sms=False)
            mem = Membership.objects.get(group=g2,user=m)
            mem.last_updated = nextd
            mem.save()

        for i in range(16,18):
            m = User.objects.create(number=str(i), allowed='y')
            streamit.add_members(g2, [m], Membership.STATUS_SUBSCRIBED, send_sms=False)
            mem = Membership.objects.get(group=g2,user=m)
            mem.last_updated = nextd
            mem.save()
        
        # make sure they don't get the old broadcast
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.create_bcasts(nextd)
        streamit.unsubscribe_by_broadcast(nextd)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(date=nextd)
        self.assertEqual(calls.count(), 0)
        
        # schedule a new broadcast
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        m4 = Message(date=nextd, content_file='foo4.mp3', user=u2)
        m4.save()
        mf4 = Message_forum(message=m4, forum=g2, status=Message_forum.STATUS_APPROVED)
        mf4.save()
        streamit.create_bcasts(nextd)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(date=nextd)
        self.assertEqual(calls.count(), 4)
        
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.create_bcasts(nextd)
        streamit.unsubscribe_by_broadcast(nextd)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(date=nextd)
        self.assertEqual(calls.count(), 4)
        
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.create_bcasts(nextd)
        streamit.unsubscribe_by_broadcast(nextd)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(date=nextd)
        self.assertEqual(calls.count(), 4)
        
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.create_bcasts(nextd)
        streamit.unsubscribe_by_broadcast(nextd)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(date=nextd)
        self.assertEqual(calls.count(), 1)
        
        # subscribe and remove some old members
        # Add 4, subtract 3
        # Total subscribers is now 14
        requested = User.objects.filter(membership__group=g2, membership__status=Membership.STATUS_REQUESTED)
        requested = [u for u in requested] 
        streamit.update_members(g2, Membership.STATUS_SUBSCRIBED, requested)
        u1 = User.objects.get(number='1')
        u2 = User.objects.get(number='2')
        u3 = User.objects.get(number='3')
        streamit.update_members(g2, Membership.STATUS_UNSUBSCRIBED, [u1,u2,u3])
        for u in requested + [u1,u2,u3]:
            mem = Membership.objects.get(group=g2, user=u)
            mem.last_updated = nextd
            mem.save()
            
        # schedule a new broadcast
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        b5date = nextd
        m5 = Message(date=nextd, content_file='foo5.mp3', user=u2)
        m5.save()
        mf5 = Message_forum(message=m5, forum=g2, status=Message_forum.STATUS_APPROVED)
        mf5.save()
        streamit.create_bcasts(nextd)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(date=nextd)
        self.assertEqual(calls.count(), 4)
        
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.create_bcasts(nextd)
        streamit.unsubscribe_by_broadcast(nextd)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(date=nextd)
        self.assertEqual(calls.count(), 4)
        
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.create_bcasts(nextd)
        streamit.unsubscribe_by_broadcast(nextd)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(date=nextd)
        self.assertEqual(calls.count(), 4)
        
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.create_bcasts(nextd)
        streamit.unsubscribe_by_broadcast(nextd)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(date=nextd)
        self.assertEqual(calls.count(), 2)
        
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.create_bcasts(nextd)
        streamit.unsubscribe_by_broadcast(nextd)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(date=nextd)
        self.assertEqual(calls.count(), 0)
        
        self.assertEqual(Call.objects.filter(date__gte=b5date, subject__number__in=[u.number for u in [u1,u2,u3]]).count(), 0)
        self.assertEqual(Survey.objects.filter(call__subject__number__in=['13','14','15']).distinct().count(), 1)
        
        # make sure unconfirmed members were not scheduled
        self.assertEqual(Call.objects.filter(subject__number=m11.number).count(), 0)
    
    def test_sms(self):
        u1 = streamit.update_user('u1','1001')
        g1 = streamit.update_group('g1', u1, 'eng')
        
        self.assertEqual(Forum.objects.filter(admin__user=u1).count(),1)   
        
        members=[]
        for i in range(10):
            m = User(number=str(i), allowed='y')
            m.save()
            members.append(m)
        m9 = User.objects.get(number=str(i))
        m9.name = ''
        m9.save()
        streamit.add_members(g1,members,send_sms=True)
        
        # check invite SMSs
        self.assertEqual(SMSMessage.objects.all().count(), 1)
        
        # should be no new invites
        streamit.update_group('g1',u1,'eng')
        streamit.update_members(g1, Membership.STATUS_SUBSCRIBED, members, send_sms=True)
        self.assertEqual(SMSMessage.objects.all().count(), 2)
        
        m11 = User.objects.create(number='11', allowed='y', name='m11')
        streamit.add_members(g1, [m11], send_sms=True)
        mem = Membership.objects.get(user=m11, group=g1)
        self.assertEqual(mem.status, Membership.STATUS_INVITED)
        streamit.update_members(g1, Membership.STATUS_SUBSCRIBED, [m11], send_sms=False)
        mem = Membership.objects.get(pk=mem.id)
        self.assertEqual(mem.status, Membership.STATUS_SUBSCRIBED)
        self.assertEqual(SMSMessage.objects.all().count(), 3)
        self.assertEqual(SMSMessage.objects.filter(sender=u1,recipients=m11).count(),1)
        self.assertEqual(g1.members.filter(number=m11.number).count(), 1)
        
        m = Message(date=datetime.now(), content_file='foo.mp3', user=u1)
        m.save()
        mf = Message_forum(message=m, forum=g1, status=Message_forum.STATUS_APPROVED)
        mf.save()
        
        now = datetime.now()
        nextyear = now.year+1
        d = datetime(year=nextyear, month=1, day=1, hour=10, minute=40)
        b1 = streamit.create_bcast_survey(mf,d)
        
        streamit.schedule_bcasts(d)
        calls = Call.objects.filter(survey=b1, date=d)
        sms = SMSMessage.objects.get(sender=u1, sent_on=d+timedelta(minutes=streamit.SMS_DELAY_MINS))
        self.assertEqual(calls.count(), 4)
        self.assertEqual(sms.recipients.all().count(), 4)
        
        line = Line.objects.get(forums__admin__user=u1)
        smstext = "New message from u1 (g1)! Call 0"+line.number+" to listen."
        
        self.assertEqual(smstext, sms.text)
        
        d += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.schedule_bcasts(d)
        d += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.schedule_bcasts(d)
        # There should be a personalized SMS and a standard
        sms = SMSMessage.objects.filter(sender=u1, sent_on=d+timedelta(minutes=streamit.SMS_DELAY_MINS))
        self.assertEqual(sms.count(), 2)
        m11sms = sms.get(recipients__in=[m11])
        self.assertEqual(m11sms.text, m11.name + ', '+smstext)
        standard = sms.exclude(recipients__in=[m11])[0]
        self.assertEqual(standard.recipients.count(), 2)
        self.assertEqual(standard.text, smstext)
        
        u2 = streamit.update_user('u2','1002')
        g2 = streamit.update_group('g2', u2, 'eng')
        streamit.add_members(g2,members,send_sms=True)
        
        u3 = streamit.update_user('u3','1003')
        g3 = streamit.update_group('g3', u3, 'eng')
        streamit.add_members(g3,members,send_sms=False)
        
        self.assertEqual(SMSMessage.objects.filter(sender=u2).count(), 1)
        self.assertEqual(SMSMessage.objects.filter(sender=u3).count(), 0)
        
        m10 = User.objects.create(number='10', allowed='y')
        m12 = User.objects.create(number='12', allowed='y')
        streamit.add_members(g2, members+[m10,m12], Membership.STATUS_SUBSCRIBED)
        # should only send sms to 3 new users
        self.assertEqual(SMSMessage.objects.filter(sender=u2).count(), 2)
        self.assertEqual(SMSMessage.objects.filter(sender=u2, recipients__in=members).distinct().count(), 1)
        
        streamit.update_members(g2, Membership.STATUS_SUBSCRIBED, members)
        # should only send to the original members (i.e. don't re-send to 10 and 12)
        self.assertEqual(SMSMessage.objects.filter(sender=u2, recipients__in=members).distinct().count(), 2)
        self.assertEqual(SMSMessage.objects.filter(sender=u2, recipients__in=[m10,m12]).distinct().count(), 1)
        
        # should send no new message (m11 not a member)
        streamit.update_members(g2, Membership.STATUS_INVITED, [m10, m11])
        streamit.update_members(g2, Membership.STATUS_SUBSCRIBED, [m10, m11])
        self.assertEqual(SMSMessage.objects.filter(sender=u2, recipients__in=[m11]).count(), 0)
        
        # should have re-sent invite and resubscribe smss to m10
        self.assertEqual(SMSMessage.objects.filter(sender=u2, recipients__in=[m10]).count(), 3)
        
    def test_bcast_type(self):
        u1 = streamit.update_user('u1','1001')
        g1 = streamit.update_group('g1', u1, 'eng')  
        
        members = []
        for i in range(10):
            m = User(number=str(i), allowed='y')
            m.save()
            members.append(m)
        streamit.add_members(g1, members, Membership.STATUS_SUBSCRIBED, send_sms=True)
            
        u2 = streamit.update_user('u2','1002')
        g2 = streamit.update_group('g2', u2, 'eng', status=Forum.STATUS_BCAST_SMS)
        self.assertEqual(Forum.objects.filter(admin__user=u2).count(),1)   
        
        streamit.add_members(g2, members, Membership.STATUS_SUBSCRIBED, send_sms=True)
        
        m = Message(date=datetime.now(), content_file='foo.mp3', user=u1)
        m.save()
        mf = Message_forum(message=m, forum=g1, status=Message_forum.STATUS_APPROVED)
        mf.save()
        
        m2 = Message(date=datetime.now(), content_file='foo2.mp3', user=u2)
        m2.save()
        mf2 = Message_forum(message=m2, forum=g2, status=Message_forum.STATUS_APPROVED)
        mf2.save()
        
        now = datetime.now()
        nextyear = now.year+1
        d = datetime(year=nextyear, month=1, day=1, hour=10, minute=40)
        
        # 2 invite SMSs
        self.assertEqual(SMSMessage.objects.all().count(), 2)
        streamit.create_and_schedule_bcast(mf, d)
        streamit.create_and_schedule_bcast(mf2, d)
        self.assertEqual(SMSMessage.objects.filter(sent_on=d).count(), 2)
        # invite + single bcast
        self.assertEqual(SMSMessage.objects.filter(sender=u2).count(), 2)
        self.assertEqual(Survey.objects.filter(number__in=[g1.line_set.all()[0].number, g2.line_set.all()[0].number]).count(), 1)
        
        streamit.update_group('g2', u2, 'eng', status=Forum.STATUS_BCAST_CALL_SMS)
        mf2 = Message_forum.objects.get(pk=mf2.id)
        streamit.create_and_schedule_bcast(mf2, d)
        self.assertEqual(Survey.objects.all().count(), 2)
        b2 = Survey.objects.get(number = g2.line_set.all()[0].number)

        nextd = datetime(year=nextyear, month=1, day=1, hour=10, minute=50)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(date=nextd)
        self.assertEqual(calls.count(), 4)
        
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(date=nextd)
        self.assertEqual(calls.count(), 4)
        
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(date=nextd)
        self.assertEqual(calls.count(), 4)
        
        nextd += timedelta(minutes=streamit.INTERVAL_MINS)
        streamit.schedule_bcasts(nextd)
        calls = Call.objects.filter(date=nextd)
        self.assertEqual(calls.count(), 4)
        
         # invite SMS plus 3 blasts
        self.assertEqual(SMSMessage.objects.filter(sender=u1).count(), 4)