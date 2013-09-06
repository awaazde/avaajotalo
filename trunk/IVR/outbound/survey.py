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
import router
from datetime import datetime, timedelta
from django.conf import settings
from otalo.surveys.models import Call, Subject
# import added below to avoid this script failing
# with the longerusername monkey patch added (not sure what the problem is)
from django.contrib.admin import actions

# This should match with how often the cron runs
INTERVAL_MINS = 1
IVR_SCRIPT = 'AO/outbound/survey.lua'
# should match the var in IVR_SCRIPT
CALLID_VAR_VAL = 'ao_survey true'

def make_calls():
     call_ids = []
     # Get all calls within the last INTERVAL
     interval = timedelta(minutes=INTERVAL_MINS)
     now = datetime.now()
 
     # get calls in the last INTERVAL
     calls = Call.objects.filter(complete=False, date__gte=now-interval, date__lt=now, machine_id=settings.MACHINE_ID).order_by('priority')
     for call in calls:
         # The way it works with backups: If we encounter a call scheduled for this run for this
         # subject, only use it if the first priority call time(s) up until this point were not
         # completed or made up
         if call.priority == 1:
             # if there is a P1, call it
             call_ids.append(call.id)
         else:
             # only make a P2 call if there have been unfullfilled P1s for this survey
             past_p1_cnt = Call.objects.filter(subject=call.subject, survey=call.survey, priority=1, date__lt=now-interval, machine_id=settings.MACHINE_ID).count()
             past_complete_cnt = Call.objects.filter(subject=call.subject, survey=call.survey, date__lt=now-interval, complete=True, machine_id=settings.MACHINE_ID).count()
             if past_p1_cnt > past_complete_cnt:
                 call_ids.append(call.id)      
     
     router.route_calls(call_ids, IVR_SCRIPT, CALLID_VAR_VAL)
                    
def main():
   make_calls()

main()
