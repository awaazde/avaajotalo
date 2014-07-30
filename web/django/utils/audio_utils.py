#===============================================================================
#    Copyright (c) 2013 awaaz.de
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

from django.conf import settings
import sys, os, time, subprocess, urllib
from datetime import datetime, timedelta
from ao.models import Message 
from surveys.models import Survey, Prompt
#from ESL import *

'''
Allow some buffer of time to look for audio to convert,
in order to avoid race conditions with remote syncing of files.

This is needed in a case where
1. A file is recorded on a remote server
2. The remote server executes an rsync within X min (where X is how often the cron runs)
3. In X + epsilon, the audio converter spots message, sees a wav file that is partially
uploaded, but begins conversion anyway.

We need to make sure conversion only happens after sync is complete.
The best way is to taskify syncing and make conversion happen after that, but
this is a temporary solution. The downside to this approach is there will
be further delay for a mp3 file to be created, hence playback in the console
will be further delayed.

The shortest you can make this BUFFER is how often the sync crons run.
If you make it longer, it is being more conservative, but it can't be any
shorter
'''
BUFFER_MINS = 2

'''Store this survey's audio locally'''
def cache_survey_audio(survey):
    con = ESLconnection('127.0.0.1', '8021', 'ClueCon')
    for p in Prompt.objects.filter(survey=survey):
        # cast to string in order for SWIG
        # to deal with unicode coming from django db
        # see http://stackoverflow.com/questions/20905702/typeerror-argument-of-type-char-const
        url = str(settings.MEDIA_URL + p.file)
        print('prefetching '+url)
        con.api("http_prefetch "+ url)
            
def convert_to_mp3(file_path):
    #converting audio file to mp3
    if ".wav" in file_path:
        to_path = file_path[:file_path.rfind(".wav")] + ".mp3"
        command = "ffmpeg -y -i %s"%(file_path) + " -f mp3 -ac 1 %s"%(to_path)
        subprocess.call(command, shell=True)
        print "converted %s"%(to_path)        
    
def convert_audio(interval_mins):
    interval = datetime.now() - timedelta(minutes=interval_mins)
    #iterating thorough all the message objects
    for m in Message.objects.filter(date__gte=interval):
        print('found message '+str(m) + ' file is '+ m.file.path)
        if '.wav' in m.file.path:
            mp3_file_path  = m.file.path[:m.file.path.rfind(".wav")] + ".mp3"
            if not os.path.isfile(mp3_file_path):
                print('converting to mp3')
                convert_to_mp3(m.file.path)
                
if __name__=="__main__":
    if "--convert_audio" in sys.argv:
        mins = sys.argv[2]
        convert_audio(int(mins))
    elif "--cache_audio" in sys.argv:
        sid = sys.argv[2]
        s = Survey.objects.get(pk=sid)
        cache_survey_audio(s)