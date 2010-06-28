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

INTERVAL_HOURS = 12
IVR_SCRIPT = 'AO/outbound/missed_call.lua'
MAX_WAIT_SECS = 12
EXEC_WAIT_SECS = 7
# since it's just a missed call, it doesn't matter which
# line we use (there is no charge)
line = Line.objects.get(pk=1)

def new_responses():
     # Get all new responses in the last INTERVAL_HOURS
     interval = timedelta(hours=INTERVAL_HOURS)
     now = datetime.now()
     
     # get messages with responses in the last INTERVAL_HOURS
     new_response_thread_ids = Message.objects.filter(lft__gt=1, date__gte=now-interval).values_list('thread', flat=True).distinct()
     # get the authors of the creators of the threads
     user_ids = User.objects.filter(message__id__in=new_response_thread_ids).values_list('id', flat=True).distinct()
     user_ids = [2] 
     #router.route_calls(user_ids, IVR_SCRIPT)
     missed_call(user_ids)

def hangup(uid):
	# hangup call
	print("hupall normal_clearing uid " + str(uid) + ": hangup command")
    	con = ESLconnection('127.0.0.1', '8021', 'ClueCon')
	con.api('hupall normal_clearing uid ' + str(uid))
	     
def missed_call(user_ids):
    con = ESLconnection('127.0.0.1', '8021', 'ClueCon')
 
    if not con.connected():
        print 'Not Connected'
        sys.exit(2)

    con.events("plain", "all");
    for uid in user_ids:
        user = User.objects.get(pk=uid)
        print('user.num= ' + user.number)
        con.api("originate {uid=" + str(uid) + "}" + str(line.dialstring_prefix) + str(user.number) +  str(line.dialstring_suffix) + " &echo")
        print(str(user.number) + ": originated call")
        # either wait for the right event or timeout, whichever comes first
        Timer(MAX_WAIT_SECS, hangup, [uid]).start()
    while 1:
        e = con.recvEvent() 
        if e:
            type = e.getType()
            print ('Type ' + type)
            if type == 'CHANNEL_STATE':
            	body = e.serialize()
            	m = re.search("Channel-State: CS_(\w+)", body)
            	if m:
                	state = m.group(1)
                	print("CHANNEL state: " + state)
            	if state == 'EXECUTE':
        		Timer(EXEC_WAIT_SECS, hangup, [uid]).start()
		if state == 'DESTROY':
            		hangup(uid)
            		break 						
def main():
    if len(sys.argv) == 2:
        responder_id = sys.argv[1]
        missed_call([responder_id])
    else:
        new_responses()

main()
