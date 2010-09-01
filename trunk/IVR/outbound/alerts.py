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
from otalo.AO.models import Message, Message_forum, User, Line, User
from otalo.surveys.models import Subject, Survey, Prompt, Option, Call
from otalo.settings import MEDIA_ROOT
from ESL import *
import re, time, sched
from threading import Timer

# These should be consistent with the constants
# in survey.lua
OPTION_NEXT = 1
OPTION_PREV = 2
OPTION_REPLAY = 3
OPTION_GOTO = 4

# should match the interval of the cron running this script
INTERVAL_HOURS = 1
SURVEY_SCRIPT = 'AO/outbound/survey.lua'
MAX_WAIT_SECS = 12
EXEC_WAIT_SECS = 7

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

def answer_call(line, userid, answer):
    prefix = line.dialstring_prefix
    suffix = line.dialstring_suffix
    
    user = User.objects.get(pk=userid)
    asker = Subject.objects.filter(number=user.number)
    if not bool(asker):
    	asker = Subject(name=user.name, number=user.number)
    	asker.save()
    else:
	    asker = asker[0]
        
    now = datetime.now()
    
    s = Survey(name="AnswerCall_" + str(asker), dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=1)
    #print ("adding announcement survey " + str(s))
    s.save()

    # welcome
    welcome = Prompt(file=line.language+"/welcome_answercall.mp3", order=1, bargein=False, survey=s)
    welcome.save()
    welcome_opt = Option(number="", action=OPTION_NEXT, prompt=welcome)
    welcome_opt.save()
    

    a = Prompt(file=MEDIA_ROOT+'/'+answer.message.content_file, order=2, bargein=False, survey=s)
    a.save()
    a_opt = Option(number="", action=OPTION_NEXT, prompt=a)
    a_opt.save()
    
    # thanks
    thanks = Prompt(file=line.language+"/thankyou_answercall.mp3", order=3, bargein=False, survey=s)
    thanks.save()
    thanks_opt = Option(number="", action=OPTION_NEXT, prompt=thanks)
    thanks_opt.save()
    
    #create a call
    call = Call(survey=s, subject=asker, date=now, priority=1)
    #print ("adding call " + str(call))
    call.save()
    
    # create calls little while from now and tommorow as backups
    onehour = timedelta(hours=1)
    call = Call(survey=s, subject=asker, date=now+onehour, priority=2)
    #print ("adding backup call " + str(call))
    call.save()
    
    tomorrow_morn = datetime(year=now.year, month=now.month, day=now.day) + timedelta(days=1, hours=7)
    call = Call(survey=s, subject=asker, date=tomorrow_morn, priority=2)
    #print ("adding backup call " + str(call))
    call.save()
    
    #make the call
    router.route_calls([call.id], SURVEY_SCRIPT)
	
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
