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
from otalo.AO.models import Message, User, Line
from ESL import *
import re, time, sched
from threading import Timer

# should match the interval of the cron running this script
INTERVAL_HOURS = 1
IVR_SCRIPT = 'AO/outbound/missed_call.lua'
MAX_WAIT_SECS = 12
EXEC_WAIT_SECS = 7

def new_responses(line, user_ids=False):
     if not user_ids:
     	# Get all new responses in the last INTERVAL_HOURS
     	interval = timedelta(hours=INTERVAL_HOURS)
     	now = datetime.now()
     
    	# Get messages with responses in the last INTERVAL_HOURS
     	new_response_thread_ids = Message.objects.filter(lft__gt=1, date__gte=now-interval, message_forum__forum__line=line).values_list('thread', flat=True).distinct()
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
	
def main():
    if len(sys.argv) > 1:
	line = sys.argv[1]
	line = Line.objects.get(pk=(int(line)))
	if len(sys.argv) > 2:
        	user_ids = sys.argv[2]
        	new_responses(line, user_ids.split(','))
	else:
		new_responses(line)
main()
