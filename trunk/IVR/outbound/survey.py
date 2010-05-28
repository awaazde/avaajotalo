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
from otalo.surveys.models import Call, Subject

INTERVAL_HOURS = 1
IVR_SCRIPT = 'AO/outbound/survey.lua'

def make_calls():
     # Get all calls within the last INTERVAL
     interval = timedelta(hours=INTERVAL_HOURS)
     now = datetime.now()
     
     # get calls in the last INTERVAL_HOURS
     subjects = Subject.objects.all()
     for subject in subjects:
         calls = Call.objects.filter(subject=subject, date__gte=now-interval).order_by('priority')
         if calls:
             call = calls[0]
             # The way it works with backups: If we encounter a call scheduled for this run for this
             # subject, only use it if the first priority call time(s) up until this point were not
             # completed or made up
             if call.priority == 1:
                 # if there is a P1, call it
                 call_ids.append(call.id)
             else:
                 # only make a P2 call if there have been unfullfilled P1s
                 past_p1_cnt = Call.objects.filter(subject=subject, priority=1, date__lt=now-interval).count()
                 past_complete_cnt = Call.objects.filter(subject=subject, date__lt=now-interval, complete=True)
                 if past_p1_cnt > past_complete_cnt and calls.count() > 1:
                     backup_call = calls[1]
                     call_ids.append(backup_call.id)      
     
     router.route_calls(call_ids, IVR_SCRIPT)
					
def main():
   make_calls()

main()
