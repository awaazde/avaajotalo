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
import os, time, subprocess
from datetime import datetime, timedelta
from ao.models import Message 

def convert_to_mp3(file_path):
    #converting audio file to mp3
    if ".wav" in file_path:
        to_path = file_path[:file_path.rfind(".wav")] + ".mp3"
        command = "ffmpeg -y -i %s"%(file_path) + " -f mp3 -ac 1 %s"%(to_path)
        subprocess.call(command, shell=True)
        print "converted %s"%(to_path)
    
def main(interval_mins):
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
    mins = sys.argv[2]
    main(int(mins))