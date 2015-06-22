#===============================================================================
#    Copyright (c) 2015 Awaaz.De Infosystems Pvt Ltd
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
from django.conf import settings
from otalo.utils import audio_utils
from otalo.ao.models import Dialer
from otalo.surveys.models import Prompt


'''
' Sync the survey prompt audio on the give machine - we need it because of survey task - before creating call, 
' we are calling this method to check if all survey files are present
'''
@shared_task(time_limit=300)
def sync_survey_audio(s, machine_id):
    is_cached = True
    for p in Prompt.objects.filter(survey=s):
        is_cached = is_cached and audio_utils.cache_audio(str(p.file))
    
    return is_cached


'''
' Sync audio file from master server in the slave machine
' file parameter is a full file path e.g. /home/awaazde/media/forum/sefc_hindi/listen.wav or stream file
' like /home/awaazde/media/2015/01/01/2015_02922323.wav
'''
@shared_task(time_limit=300)
def sync_audio_file(file, machine_id):
    audio_utils.cache_audio(file)

