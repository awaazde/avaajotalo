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
from otalo.AO.models import Message_responder

IVR_SCRIPT = 'AO/outbound/missed_call.lua'
INTERVAL_HOURS = 12

def new_responses():
     # Get all new responses in the last INTERVAL_HOURS
     interval = timedelta(hours=INTERVAL_HOURS)
     now = datetime.now()
     
     # get messages with responses in the last INTERVAL_HOURS
     new_response_thread_ids = Message.objects.filter(lft__gt=1, date__gte=now-interval).values_list('thread', flat=True).distinct()
     # get the authors of the creators of the threads
     user_ids = User.objects.filter(message__id__in=new_response_thread_ids).values_list('id', flat=True).distinct()
     
     router.route_calls(user_ids, IVR_SCRIPT)

def main():
   new_reponses()

main()
