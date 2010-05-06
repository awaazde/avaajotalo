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
import sys
import time
from datetime import datetime
from ESL import *
from otalo.AO.models import Message_responder

IVR_script = 'AO/outbound/answer.lua'
MAX_CHANNELS = 10

def main():
    # check for expired reserve_untils and release them
    now = datetime.now()
    Message_responder.objects.filter(reserved_until__lt=now).update(reserved_by=None, reserved_until=None)
    
    con = ESLconnection('127.0.0.1', '8021', 'ClueCon')
    
    if not con.connected():
	print 'Not Connected'
	sys.exit(2)

    # get every possible responder and let the script figure out which messages to play, etc.
    responder_ids = Message_responder.objects.values_list('user', flat=True).distinct()
    
    for responder_id in responder_ids:
        # only make a call when we are below the threshold
	# to avoid worrying about race conditions, provision
	# enough cushion in the threshold by making it conservative
	num_channels = get_n_channels(con)
	sleep_secs = 2
	while (num_channels >= MAX_CHANNELS):
	   #sleep for a while
	   print("too many channels: " + str(num_channels) + ", sleeping for " + str(sleep_secs) + "s")
	   time.sleep(sleep_secs)
           num_channels = get_n_channels(con)
	   sleep_secs *= 2
	
	print('num channels: ' + str(num_channels))
	con.api("luarun " + IVR_script + " " + str(responder_id))
	# sleep a bit to let the call register with FS
	time.sleep(2)
	   
def get_n_channels(con):
    e = con.api("show channels")
    chan_txt = e.getBody()
    n_chans_txt = chan_txt[chan_txt.rindex('total.')-3:chan_txt.rindex('total.')-1]
    return int(n_chans_txt)    

main()
