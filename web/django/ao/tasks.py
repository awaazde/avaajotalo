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
from datetime import datetime, timedelta
from celery import shared_task
from haystack.management.commands import update_index
from otalo.utils import audio_utils
import broadcast
from otalo.ao.models import Dialer
from otalo.surveys.models import Prompt

'''
'    Helper function to run periodic tasks with the scheduler
'    Don't run as a subtask since it's just a helper
'''
@shared_task(time_limit=300)
def schedule_bcasts_by_dialers(*dialerids):
    dialers = Dialer.objects.all()
    if dialerids:
        dialers = dialers.filter(pk__in=dialerids)
        
    schedule_bcasts(dialers=dialers)
    
'''
'    Helper function to run periodic tasks with the scheduler
'    Don't run as a subtask since it's just a helper
'''
@shared_task
def schedule_bcasts_by_basenums(*numbers):
    dialers = Dialer.objects.filter(base_numbers__in=numbers)
    
    schedule_bcasts(dialers=dialers)
    
'''
'    A periodic task that gets surveys and creates
'    calls. Why periodic? Because we need to run the scheduling
'    algorithm on calls to prioritize which go out first between bcasts
'    over a given dialer.
'
'    Doing it here higher up in the app logic to keep the actual
'    dialer tasks as pure and simple as possible. Assume nothing
'    about how calls should go out, just send them out.
'''
@shared_task
def schedule_bcasts(time=None, dialers=None):
    broadcast.schedule_bcasts(time, dialers)
    
'''
'    To send responses that were not triggered through
'    the web (i.e. an admin records a response over IVR)
'''
@shared_task
def response_calls(interval_mins):
    broadcast.check_unsent_responses(interval_mins)

'''
'    Convert mp3 to wav files
'''
@shared_task
def convert_audio(interval_mins):
    audio_utils.convert_audio(interval_mins)
    
'''
'    Stash audio for this survey at the
'    machines it may play at
'''
@shared_task
def cache_survey_audio(s, dialers=None):
    machine_ids = []
    if not dialers:
        dialers = s.dialers.all()
    for d in dialers:
        machine_ids.append(d.machine_id)
        machine_ids = list(set(machine_ids))
    
    for mid in machine_ids:
        cache_audio.s().delay(s, mid)

'''
'   Download audio file from master server at this machine
'''
@shared_task
def cache_audio(s, machine_id):
    is_cached = True
    for p in Prompt.objects.filter(survey=s):
        is_cached = is_cached and audio_utils.cache_survey_audio(str(p.file))
    
    return is_cached


'''
' Download audio file from master server at this machine
'''
@shared_task
def cache_audio_file(file, machine_id):
    audio_utils.cache_survey_audio(file)

'''
' Download audio file from master server at this machine
'''
@shared_task
def cache_message_audio(mf, machine_id):
    audio_utils.cache_survey_audio(re.sub('\\' + settings.MEDIA_ROOT + '$', '', str(mf.message.file)))

        
'''
'    Update haystack search index
'''
@shared_task(time_limit=300)
def update_search_index(interval_hours):
    update_index.Command().handle(age=interval_hours)



@shared_task
def sync_media(file):
    audio_utils.sync_media(file)