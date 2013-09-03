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
import sys,router
from datetime import datetime, timedelta
from django.db.models import Q
from otalo.ao.models import Message, Message_forum, User, Line, User
from otalo.surveys.models import Subject, Survey, Prompt, Option, Call, Param
from otalo.settings import MEDIA_ROOT
#from ESL import *
import re, time, sched
from threading import Timer

# should match the interval of the cron running this script
INTERVAL_HOURS = 1
SURVEY_SCRIPT = 'AO/outbound/survey.lua'
MAX_WAIT_SECS = 12
EXEC_WAIT_SECS = 7

def unsent_responses():
    interval = timedelta(hours=INTERVAL_HOURS)
    now = datetime.now()
    # Get responses in the last INTERVAL_HOURS
    responses = Message_forum.objects.filter(message__lft__gt=1, message__date__gte=now-interval, status=Message_forum.STATUS_APPROVED)
    for response in responses:
        if not Prompt.objects.filter(file__contains=response.message.content_file):
            answer_call(response.forum.line_set.all()[0], response)
            
def hangup(uid):
	# hangup call
	#print("hupall normal_clearing uid " + str(uid) + ": hangup command")
    con = ESLconnection('127.0.0.1', '8021', 'ClueCon')
    con.api('hupall normal_clearing uid ' + str(uid))
    con.disconnect()
	     
def missed_call(line, user_ids):
    for uid in user_ids:
    	con = ESLconnection('127.0.0.1', '8021', 'ClueCon')
    	con.events("plain", "all");
        user = User.objects.get(pk=uid)
	#print("originate {uid=" + str(uid) + "}" + str(line.dialstring_prefix) + str(user.number) +  str(line.dialstring_suffix) + " &echo")
        con.api("originate {uid=" + str(uid) + "}" + str(line.dialstring_prefix) + str(user.number) +  str(line.dialstring_suffix) + " &echo")
        #print(str(user.number) + ": originated call")
        # either wait for the right event or timeout, whichever comes first
        Timer(MAX_WAIT_SECS, hangup, [uid]).start()
    	while 1:
        	e = con.recvEvent() 
        	if e:
            		type = e.getType()
            		#print ('Type ' + type)
            		if type == 'CHANNEL_STATE':
            			body = e.serialize()
            			m = re.search("Channel-State: CS_(\w+)", body)
            			if m:
                			state = m.group(1)
                			#print("CHANNEL state: " + state)
            				if state == 'EXECUTE':
        					Timer(EXEC_WAIT_SECS, hangup, [uid]).start()
					if state == 'DESTROY':
            					hangup(uid)
            					break 						
	con.disconnect()

def answer_call(line, answer):
    # get the immediate parent of this message
    fullthread = Message.objects.filter(Q(thread=answer.message.thread) | Q(pk=answer.message.thread.pk))
    ancestors = fullthread.filter(lft__lt=answer.message.lft, rgt__gt=answer.message.rgt).order_by('-lft')
    parent = ancestors[0]

    asker = Subject.objects.filter(number=parent.user.number)
    if not bool(asker):
    	asker = Subject.objects.create(name=parent.user.name, number=parent.user.number)
    else:
	    asker = asker[0]
        
    now = datetime.now()
    num = line.outbound_number or line.number
        
    s = Survey.objects.create(broadcast=True, name=Survey.ANSWER_CALL_DESIGNATOR +'_' + str(asker), complete_after=0, number=num, created_on=now, backup_calls=1)
    s.subjects.add(asker)
    #print ("adding announcement survey " + str(s))
    order = 1
    
    # welcome
    welcome = Prompt.objects.create(file=line.language+"/welcome_responsecall.wav", order=order, bargein=True, survey=s)
    welcome_opt = Option.objects.create(number="", action=Option.NEXT, prompt=welcome)
    welcome_opt2 = Option.objects.create(number="1", action=Option.NEXT, prompt=welcome)
    order += 1
    
    original = Prompt.objects.create(file=MEDIA_ROOT+'/'+parent.content_file, order=order, bargein=True, survey=s)
    original_opt = Option.objects.create(number="", action=Option.NEXT, prompt=original)
    original_opt2 = Option.objects.create(number="1", action=Option.NEXT, prompt=original)
    order += 1
    
    response = Prompt.objects.create(file=line.language+"/response_responsecall.wav", order=order, bargein=True, survey=s)
    response_opt = Option.objects.create(number="", action=Option.NEXT, prompt=response)
    response_opt2 = Option.objects.create(number="1", action=Option.NEXT, prompt=response)
    order += 1
        

    a = Prompt.objects.create(file=MEDIA_ROOT+'/'+answer.message.content_file, order=order, bargein=True, survey=s)
    a_opt = Option.objects.create(number="", action=Option.NEXT, prompt=a)
    a_opt2 = Option.objects.create(number="1", action=Option.NEXT, prompt=a)
    order += 1
    
    if answer.forum.respondtoresponse_allowed:
        record = Prompt.objects.create(file=line.language+"/record_responsecall.wav", order=order, bargein=True, survey=s, delay=3000)
        record_opt = Option.objects.create(number="", action=Option.GOTO, prompt=record)
        param = Param.objects.create(option=record_opt, name=Param.IDX, value=order+2)
        record_opt2 = Option.objects.create(number="1", action=Option.RECORD, prompt=record)
        param2 = Param.objects.create(option=record_opt2, name=Param.MFID, value=answer.id)
        param3 = Param.objects.create(option=record_opt2, name=Param.ONCANCEL, value=order+2)
        order += 1
        
        recordthanks = Prompt.objects.create(file=line.language+"/thankyourecord_responsecall.wav", order=order, bargein=True, survey=s, delay=0)
        recordthanks_opt = Option.objects.create(number="", action=Option.NEXT, prompt=recordthanks)
        order += 1
    
    # thanks
    thanks = Prompt.objects.create(file=line.language+"/thankyou_responsecall.wav", order=order, bargein=True, survey=s)
    thanks_opt = Option.objects.create(number="", action=Option.NEXT, prompt=thanks)
    order += 1
	
def main():
	unsent_responses()

main()
