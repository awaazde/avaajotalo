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
import time, re
from datetime import datetime
from django.db import IntegrityError
from celery.exceptions import MaxRetriesExceededError
from celery import shared_task
from celery.task.control import revoke
from otalo.ao.models import Dialer
import otalo.tasks
from otalo.surveys.models import Call, Survey
from ESL import *


BCAST_SCRIPT= 'AO/outbound/survey.lua'
   
@shared_task(time_limit=300)
def schedule_call(survey, dialer, subject, priority):
    con = ESLconnection('127.0.0.1', '8021', 'ClueCon')
    # reload survey to check status for cancellation
    survey = Survey.objects.get(pk=survey.id)
    
    '''
    ' Making sure that all the required survey audio files present locally, if its not then skipping the scheduling for now
    '''
    cached = otalo.tasks.sync_survey_audio(survey, dialer.machine_id)
    
    '''
    '    Do congestion control down here because we assume
    '    higher level schedulers are *not* sending tasks based on
    '    the available resources. Schedulers may just be sending
    '    according to the dialers max_parallel_out, not knowing about
    '    other schedulers working with the same dialer are doing the same.
    '    Why are there multiple schedulers? Because there are different kinds
    '    of calls that may be sent at different priorities. Having different
    '    schedulers handle different types of calls allows them to be prioritized
    '    according to call type (within a scheduler, calls of the same type
    '    can be prioritized between each other).
    '        
    '    Another reason for congestion control down here is efficiency.
    '    A higher-level scheduler can at best schedule calls up to max_parallel_out
    '    every interval, but we should be able to send the next call as soon as
    '    a channel is free. Since this task is not on beat, it can opportunistically
    '    look for free channels and send a call out accordingly. This can come into
    '    play if schedulers schedule more calls than max_parallel_out per beat
    '
    '    Note calls piling up due to physical dialing resource downtime (i.e. FS) is *not* a reason
    '    for congestion control here, since we are only creating calls if we can connect via ESL.
    '
    '    Have check to make sure Call doesn't already exist. Multiple tasks with the same
    '    Call params can happen if:
    '    a) you have multiple dialers spanning the same number range but connected to different
    '        physical dialers, and the scheduler doesn't check that the same call is schedule across
    '        different dialers
    '    b) the calls queue is backed up and the same scheduler attempts to schedule the same call repeatedly
    '    
    '    Because of the second reason, it's not enough to keep track of scheduled calls in one rev of
    '    a scheduler that manages multiple dialers, because on the next rev if the previous task is
    '    still in the queue, it will get double-scheduled. How can the calls queue get backed up? If
    '    for some reason the worker on a calls queue goes down but the scheduler stays alive. This is more
    '    likely to happen with call queues on remote machines.
    '
    '    We never want to have a call be double-scheduled, so take a hit and do the db query here.
    '    Note the query should *not* filter by dialer, since we want to check for the call across all dialers
    
    '    UPDATE: It is not enough to do a db check for whether the call obj has already been created, because of multi-worker
    '    race condition. Imagine the same task is scheduled in two different queues. If both of those tasks enter at the
    '    same time, their db sessions (transactions) would not be able to update against each other and both could
    '    create the object. Django's get_or_create is also not threadsafe: http://stackoverflow.com/questions/6416213/is-get-or-create-thread-safe
    
    '    To prevent the race condition, have to enforce consistency at the DB level through
    '    unique constraints. Account for the db constraint here by catching the error and simply moving on if it happens.
    '''
    if cached and con.connected() and get_n_channels(con, dialer) < dialer.max_parallel_out and survey.status != Survey.STATUS_CANCELLED:
        try:
            call = Call.objects.create(survey=survey, dialer=dialer, subject=subject, priority=priority, date=datetime.now())
            
            command = "luarun " + BCAST_SCRIPT + " " + str(call.id)
            con.bgapi(command)
            print('Scheduled call '+ str(call))
        
            '''
            # insert any additionally required gap
            # to the queue's natural gap (based on concurrency settings)
            # for physical dialing resource to keep up
            # Do it here since higher level schedulers would get too complicated
            # managing chains of calls based on common queues
            # As long as sleeping in a task is safe, this is simpler since
            # the task itself will implement the gap it needs to in whatever queue it is in
            '''
            time.sleep(dialer.call_gap_secs or Dialer.DEFAULT_CALL_GAP_SECS)
            
        except IntegrityError as e:
            print(e)
            pass
        
    '''
    '    Don't worry about retrying... the higher level scheduling algorithm should be 
    '    keeping track dynamically of what got scheduled and what didn't through a combo of:
    '        * beating, so it's trying to pump the queue regularly
    '        * checking for created Call objects.
    '''

@shared_task
def test_task(survey, dialer, subject, priority, date):
    if not bool(Call.objects.filter(survey=survey, subject=subject, priority=priority)):
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
    #print("profile is "+profile)
   
    e = con.api(profile)
    chan_txt = e.getBody()
    n_chans_txt = chan_txt[chan_txt.rindex('total.')-3:chan_txt.rindex('total.')-1]
    return int(n_chans_txt)
