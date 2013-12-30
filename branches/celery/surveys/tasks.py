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
import re, time
from datetime import datetime
from celery.exceptions import MaxRetriesExceededError
from celery import shared_task
from celery.task.control import revoke
from otalo.ao.models import Dialer
from otalo.surveys.models import Call, Survey
from ESL import *


BCAST_SCRIPT= 'AO/outbound/survey.lua'
BCAST_ESL_GAP_SECS = .3
RETRY_COUNTDOWN_SECS = 120
   
@shared_task(bind=True)
def schedule_call(self, survey, dialer, subject, priority):
    call = Call.objects.create(survey=survey, dialer=dialer, subject=subject, priority=priority, date=datetime.now())
    con = ESLconnection('127.0.0.1', '8021', 'ClueCon')
    '''
    '    Do a final check for open channels here even though we assume
    '    higher level schedulers are doing the congestion control. The reason
    '    is that if the dialer disconnects (i.e. FS goes down), the queue will
    '    fill up with backlogged calls as the scheduler continues to work. 
    '    So this task will have to perform congestion
    '    control in that case until the backlog naturally reduces.
    '    In other words, the queue itself should not be relied on to determine
    '    how many calls to make (i.e. there are 100 calls in the queue so we should make 100 calls)
    '''
    if con.connected() and get_n_channels(con, dialer) < dialer.max_parallel_out and survey.status != Survey.STATUS_CANCELLED:
        command = "luarun " + BCAST_SCRIPT + " " + str(call.id)
        con.api(command)
        print('Scheduled call '+ str(call))
        # insert a gap between calls for the
        # physical dialing resource to keep up
        time.sleep(BCAST_ESL_GAP_SECS)
    elif survey.status != Survey.STATUS_CANCELLED:
        print("retrying "+ command) 
        raise self.retry(countdown=RETRY_COUNTDOWN_SECS)

@shared_task(bind=True)
def test_task(self, survey, dialer, subject, priority, date, retry=False):
    call = Call.objects.create(survey=survey, dialer=dialer, subject=subject, priority=priority, date=date)
    print('Scheduled call '+ str(call))
    #print("task "+str(self)+"-"+str(test_task.request.id))
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