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
import sys
from datetime import datetime, timedelta
from otalo.AO.models import Line
from otalo.surveys.models import Survey, Subject, Call, Prompt, Option
from random import shuffle
import broadcast

# These should be consistent with the constants
# in survey.lua
OPTION_NEXT = 1
OPTION_PREV = 2
OPTION_REPLAY = 3
OPTION_GOTO = 4
OPTION_RECORD = 5;

SOUND_EXT = ".wav"

def thread_template(line):
    prefix = line.dialstring_prefix
    suffix = line.dialstring_suffix
    language = line.language
    if line.outbound_number:
        num = line.outbound_number
    else:
        num = line.number
    
    name = line.name + '_THREAD_' + broadcast.TEMPLATE_DESIGNATOR
    
    s = Survey.objects.filter(name=name)
    if not bool(s):
        s = Survey(name=name, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0, number=num, template=True)
        print ("adding template " + str(s))
        s.save()
    
        # welcome
        welcome = Prompt(file=language+"/welcome_thread"+SOUND_EXT, order=1, bargein=False, survey=s)
        welcome.save()
        welcome_opt = Option(number="", action=OPTION_NEXT, prompt=welcome)
        welcome_opt.save()
        
        # thanks
        thanks = Prompt(file=language+"/thankyou_thread"+SOUND_EXT, order=3, bargein=True, delay=5000, survey=s)
        thanks.save()
        thanks_opt1 = Option(number="9", action=OPTION_GOTO, action_param1=2, prompt=thanks)
        thanks_opt1.save()
        thanks_opt2 = Option(number="", action=OPTION_NEXT, prompt=thanks)
        thanks_opt2.save()
        
        return s
    else:
        return s[0]  

def qna_template(line):
    prefix = line.dialstring_prefix
    suffix = line.dialstring_suffix
    language = line.language
    if line.outbound_number:
        num = line.outbound_number
    else:
        num = line.number
    
    name = line.name + '_QNA_' + broadcast.TEMPLATE_DESIGNATOR
    
    s = Survey.objects.filter(name=name)
    if not bool(s):
        s = Survey(name=name, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0, number=num, template=True)
        print ("adding template " + str(s))
        s.save()
    
        # welcome
        welcome = Prompt(file=language+"/welcome_bcast"+SOUND_EXT, order=1, bargein=True, survey=s)
        welcome.save()
        welcome_opt = Option(number="", action=OPTION_NEXT, prompt=welcome)
        welcome_opt.save()
        welcome_opt2 = Option(number="1", action=OPTION_NEXT, prompt=welcome)
        welcome_opt2.save()
        
        # qna
        qna = Prompt(file=language+"/qna"+SOUND_EXT, order=2, bargein=True, survey=s)
        qna.save()
        qna_opt = Option(number="", action=OPTION_NEXT, prompt=qna)
        qna_opt.save()
        qna_opt2 = Option(number="1", action=OPTION_NEXT, prompt=qna)
        qna_opt2.save()
        
        # motivation
        motivation = Prompt(file=language+"/recordmotivation"+SOUND_EXT, order=4, bargein=True, survey=s, delay=1000)
        motivation.save()
        motivation_opt = Option(number="", action=OPTION_NEXT, prompt=motivation)
        motivation_opt.save()
        motivation_opt2 = Option(number="1", action=OPTION_NEXT, prompt=motivation)
        motivation_opt2.save()
        
        # record
        record = Prompt(file=language+"/recordmessage"+SOUND_EXT, order=5, bargein=False, survey=s, delay=1000, name='Response')
        record.save()
        record_opt = Option(number="", action=OPTION_RECORD, prompt=record)
        record_opt.save()
        
        # thanks
        thanks = Prompt(file=language+"/recordthankyou"+SOUND_EXT, order=6, bargein=True, delay=5000, survey=s)
        thanks.save()
        thanks_opt = Option(number="", action=OPTION_NEXT, prompt=thanks)
        thanks_opt.save()
        
        return s
    else:
        return s[0]  
        
def main():
    line = Line.objects.get(pk=1)
    thread_template(line)
    qna_template(line)
    
main()

