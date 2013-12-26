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
import re
from celery.exceptions import MaxRetriesExceededError
from celery import shared_task
from celery.task.control import revoke
from otalo.ao.models import Dialer
from ESL import *


BCAST_SCRIPT= 'AO/outbound/survey.lua'
BCAST_ESL_GAP_SECS = .3
RETRY_COUNTDOWN_SECS = 120
   
'''
'    Make dialer a separate arg for optimization purposes
'    save a lookup if it's passed in directly
'''
@shared_task(bind=True)
def schedule_call(self, call, dialer=None):
    con = ESLconnection('127.0.0.1', '8021', 'ClueCon')
    if not dialer:
        dialer = call.dialer
    if con.connected() and get_n_channels(con, dialer) <= dialer.max_parallel_out:
        con.api("luarun " + BCAST_SCRIPT + " " + str(call.id))
        # insert a gap between calls for the
        # actual dialing resource to keep up
        time.sleep(BCAST_ESL_GAP_SECS)
    else:
        raise self.retry(countdown=RETRY_COUNTDOWN_SECS)

@shared_task(bind=True)
def test_task(self, retry=False):
    print("task "+str(self)+"-"+str(test_task.request.id))
    if retry:
        try:
            print("retrying")
            raise self.retry(countdown=RETRY_COUNTDOWN_SECS)
        except MaxRetriesExceededError as e:
            print('max retries')
            revoke(test_task.request.id)
            pass

'''
'    Mirrors get_num_channels in common.lua(s)
'''
def get_n_channels(con, dialer):
    if dialer.type == Dialer.TYPE_PRI:
        profile = re.match('[\w/\d]+grp(\d+)[\w/\d]+',dialer.dialstring_prefix).groups()[0]
        profile = "FreeTDM/" + str(profile)
    else:
        '''
        '    SIP
        '    ASSUMES profile name is same as gateway name
        '    FS show channels names calls by profile name, not gateway name.
        '    so if we need multiple gateways in a profile that could be a problem 
        '    if it there is not physical limit to SIP calls, safe to not worry about
        '    naming the gateway in any particular way
        '
        '''
        profile = re.match('sofia/gateway/([\w\d-]+)',dialer.dialstring_prefix).groups()[0]
        profile = "sofia/" + str(profile)
    
    profile = "show channels like " + profile
    print("profile is "+profile)
    
    e = con.api(profile)
    chan_txt = e.getBody()
    n_chans_txt = chan_txt[chan_txt.rindex('total.')-3:chan_txt.rindex('total.')-1]
    return int(n_chans_txt)