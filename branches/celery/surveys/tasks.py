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
   
@shared_task
def schedule_call(survey, dialer, subject, priority):
    con = ESLconnection('127.0.0.1', '8021', 'ClueCon')
    # reload survey to check status for cancellation
    survey = Survey.objects.get(pk=survey.id)
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
        call = Call.objects.create(survey=survey, dialer=dialer, subject=subject, priority=priority, date=datetime.now())
        command = "luarun " + BCAST_SCRIPT + " " + str(call.id)
        con.api(command)
        print('Scheduled call '+ str(call))
        # insert a gap between calls for the
        # physical dialing resource to keep up
        time.sleep(BCAST_ESL_GAP_SECS)
        
    '''
    '    Don't worry about retrying... the higher level scheduling algorithm should be 
    '    keeping track dynamically of what got scheduled and what didn't through a combo of:
    '        * beating, so it's trying to pump the queue regularly
    '        * checking for created Call objects.
    '''

@shared_task
def test_task(survey, dialer, subject, priority, date):
    call = Call.objects.create(survey=survey, dialer=dialer, subject=subject, priority=priority, date=date)
    print('Scheduled call '+ str(call))

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