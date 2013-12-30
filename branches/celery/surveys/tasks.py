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
import time
from datetime import datetime
from celery.exceptions import MaxRetriesExceededError
from celery import shared_task
from celery.task.control import revoke
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
    '    Do not do any congestion control down here because we assume
    '    Higher level schedulers are beating and sending tasks based on
    '    the available resources. In addition, calls won't pile up due to
    '    physical dialing resource downtime (i.e. FS) since we are only creating
    '    calls if we can connect via ESL.
    '''
    if con.connected() and survey.status != Survey.STATUS_CANCELLED:
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