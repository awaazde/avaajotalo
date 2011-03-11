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
from otalo.AO.models import Message, Message_forum, User, Line, User
from otalo.surveys.models import Subject, Survey, Prompt, Option, Call, Param
from otalo.settings import MEDIA_ROOT
from ESL import *
import re, time, sched
from threading import Timer

# should match the interval of the cron running this script
INTERVAL_HOURS = 1
SURVEY_SCRIPT = 'AO/outbound/survey.lua'
MAX_WAIT_SECS = 12
EXEC_WAIT_SECS = 7

ANSWER_CALL_DESIGNATOR = "AnswerCall_"

def new_responses(line, user_ids=False):
     if not user_ids:
     	# Get all new responses in the last INTERVAL_HOURS
     	interval = timedelta(hours=INTERVAL_HOURS)
     	now = datetime.now()
     
    	# Get responses in the last INTERVAL_HOURS
     	new_response_thread_ids = Message.objects.filter(lft__gt=1, date__gte=now-interval, message_forum__forum__line=line, message_forum__status=MESSAGE_STATUS_APPROVED).values_list('thread', flat=True).distinct()
     	# Get the authors of the creators of the threads
     	user_ids = User.objects.filter(message__id__in=new_response_thread_ids).values_list('id', flat=True).distinct()
     
     missed_call(line, user_ids)

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
    prefix = line.dialstring_prefix
    suffix = line.dialstring_suffix
    
    # get the immediate parent of this message
    fullthread = Message.objects.filter(Q(thread=answer.message.thread) | Q(pk=answer.message.thread.pk))
    ancestors = fullthread.filter(lft__lt=answer.message.lft, rgt__gt=answer.message.rgt).order_by('-lft')
    parent = ancestors[0]

    asker = Subject.objects.filter(number=parent.user.number)
    if not bool(asker):
    	asker = Subject(name=parent.user.name, number=parent.user.number)
    	asker.save()
    else:
	    asker = asker[0]
        
    now = datetime.now()
    
    if line.outbound_number:
        num = line.outbound_number
    else:
        num = line.number
        
    s = Survey(name=ANSWER_CALL_DESIGNATOR + str(asker), dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0, number=num)
    #print ("adding announcement survey " + str(s))
    s.save()
    order = 1
    
    # welcome
    welcome = Prompt(file=line.language+"/welcome_responsecall.wav", order=order, bargein=True, survey=s)
    welcome.save()
    welcome_opt = Option(number="", action=Option.NEXT, prompt=welcome)
    welcome_opt.save()
    welcome_opt2 = Option(number="1", action=Option.NEXT, prompt=welcome)
    welcome_opt2.save()
    order += 1
    
    # NOTE: This conditional is for legacy purposes only. Once everyone records the new responsecall set
    # this if should go away
    if answer.forum.respondtoresponse_allowed: 
        original = Prompt(file=MEDIA_ROOT+'/'+parent.content_file, order=order, bargein=True, survey=s)
        original.save()
        original_opt = Option(number="", action=Option.NEXT, prompt=original)
        original_opt.save()
        original_opt2 = Option(number="1", action=Option.NEXT, prompt=original)
        original_opt2.save()
        order += 1
        
        response = Prompt(file=line.language+"/response_responsecall.wav", order=order, bargein=True, survey=s)
        response.save()
        response_opt = Option(number="", action=Option.NEXT, prompt=response)
        response_opt.save()
        response_opt2 = Option(number="1", action=Option.NEXT, prompt=response)
        response_opt2.save()
        order += 1
        

    a = Prompt(file=MEDIA_ROOT+'/'+answer.message.content_file, order=order, bargein=True, survey=s)
    a.save()
    a_opt = Option(number="", action=Option.NEXT, prompt=a)
    a_opt.save()
    a_opt2 = Option(number="1", action=Option.NEXT, prompt=a)
    a_opt2.save()
    order += 1
    
    if answer.forum.respondtoresponse_allowed:
        record = Prompt(file=line.language+"/record_responsecall.wav", order=order, bargein=True, survey=s, delay=3000)
        record.save()
        record_opt = Option(number="", action=Option.GOTO, prompt=record)
        record_opt.save()
        param = Param(option=record_opt, name=Param.IDX, value=order+2)
        param.save()
        record_opt2 = Option(number="1", action=Option.RECORD, prompt=record)
        record_opt2.save()
        param2 = Param(option=record_opt2, name=Param.MFID, value=answer.id)
        param2.save()
        param3 = Param(option=record_opt2, name=Param.ONCANCEL, value=order+2)
        param3.save()
        order += 1
        
        recordthanks = Prompt(file=line.language+"/thankyourecord_responsecall.wav", order=order, bargein=True, survey=s)
        recordthanks.save()
        recordthanks_opt = Option(number="", action=Option.NEXT, prompt=recordthanks)
        recordthanks_opt.save()
        order += 1
    
    # thanks
    thanks = Prompt(file=line.language+"/thankyou_responsecall.wav", order=order, bargein=True, survey=s)
    thanks.save()
    thanks_opt = Option(number="", action=Option.NEXT, prompt=thanks)
    thanks_opt.save()
    order += 1
    
    #create a call
    call = Call(survey=s, subject=asker, date=now, priority=1)
    #print ("adding call " + str(call))
    call.save()
    
    # create calls little while from now and tommorow as backups
    onehour = timedelta(hours=1)
    call = Call(survey=s, subject=asker, date=now+onehour, priority=2)
    #print ("adding backup call " + str(call))
    call.save()
    
    tomorrow_morn = datetime(year=now.year, month=now.month, day=now.day) + timedelta(days=1, hours=9)
    call = Call(survey=s, subject=asker, date=tomorrow_morn, priority=2)
    #print ("adding backup call " + str(call))
    call.save()
    
	
def main():
    if len(sys.argv) > 1:
	line = sys.argv[1]
	line = Line.objects.get(pk=int(line))
	if len(sys.argv) > 2:
		if len(sys.argv) > 3:
			user_id = sys.argv[2]
			mfid = sys.argv[3]
			mf = Message_forum.objects.get(pk=int(mfid))
			answer_call(line,int(user_id),mf)
		else:
			user_ids = sys.argv[2].split(',')
        		#new_responses(line, user_ids.split(','))
			missed_call(line, user_ids)
	else:
		new_responses(line)
#main()
