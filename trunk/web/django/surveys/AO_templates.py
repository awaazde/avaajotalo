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
OPTION_RECORD = 5
OPTION_INPUT = 6
OPTION_TRANSFER = 7

SOUND_EXT = ".wav"

def standard_template(line, contenttype):
    prefix = line.dialstring_prefix
    suffix = line.dialstring_suffix
    language = line.language
    if line.outbound_number:
        num = line.outbound_number
    else:
        num = line.number
    
    name = contenttype[:3].upper() + '_' + broadcast.TEMPLATE_DESIGNATOR + ' (' + str(line.id) + ')'
    
    s = Survey.objects.filter(name=name)
    if not bool(s):
        s = Survey(name=name, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0, number=num, template=True)
        print ("adding template " + str(s))
        s.save()
    
        # welcome
        welcome = Prompt(file=language+"/welcome"+SOUND_EXT, order=1, bargein=False, survey=s)
        welcome.save()
        welcome_opt1 = Option(number="", action=OPTION_NEXT, prompt=welcome)
        welcome_opt1.save()
        welcome_opt2 = Option(number="1", action=OPTION_NEXT, prompt=welcome)
        welcome_opt2.save()
        
        # content
        content = Prompt(file=language+"/"+contenttype+SOUND_EXT, order=2, bargein=True, survey=s)
        content.save()
        content_opt = Option(number="", action=OPTION_NEXT, prompt=content)
        content_opt.save()
        content_opt2 = Option(number="1", action=OPTION_NEXT, prompt=content)
        content_opt2.save()
        
        # thanks
        thanks = Prompt(file=language+"/thankyou"+SOUND_EXT, order=4, bargein=True, delay=5000, survey=s)
        thanks.save()
        thanks_opt1 = Option(number="", action=OPTION_NEXT, prompt=thanks)
        thanks_opt1.save()
        thanks_opt2 = Option(number="1", action=OPTION_NEXT, prompt=thanks)
        thanks_opt2.save()
        
        return s
    else:
        return s[0] 
     
def freecall_template(line, contenttype): 
    prefix = line.dialstring_prefix
    suffix = line.dialstring_suffix
    language = line.language
    if line.outbound_number:
        num = line.outbound_number
    else:
        num = line.number
    
    name = contenttype[:3] +'_CALL_' + broadcast.TEMPLATE_DESIGNATOR
    
    s = Survey.objects.filter(name=name)
    if not bool(s):
        s = Survey(name=name, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0, number=num, template=True)
        print ("adding template " + str(s))
        s.save()
    
        # welcome
        welcome = Prompt(file=language+"/welcome_bcast"+SOUND_EXT, order=1, bargein=True, survey=s, delay=0)
        welcome.save()
        welcome_opt = Option(number="", action=OPTION_NEXT, prompt=welcome)
        welcome_opt.save()
        welcome_opt2 = Option(number="1", action=OPTION_NEXT, prompt=welcome)
        welcome_opt2.save()
        
        # content
        content = Prompt(file=language+"/"+contenttype+SOUND_EXT, order=2, bargein=True, survey=s)
        content.save()
        content_opt = Option(number="", action=OPTION_NEXT, prompt=content)
        content_opt.save()
        content_opt2 = Option(number="1", action=OPTION_NEXT, prompt=content)
        content_opt2.save()
        
        # motivation
        motivation = Prompt(file=language+"/recordmotivation"+SOUND_EXT, order=4, bargein=True, survey=s, delay=0)
        motivation.save()
        motivation_opt = Option(number="", action=OPTION_NEXT, prompt=motivation)
        motivation_opt.save()
        motivation_opt2 = Option(number="1", action=OPTION_NEXT, prompt=motivation)
        motivation_opt2.save()
        
        # freecall
        freecall = Prompt(file=language+"/freecall"+SOUND_EXT, order=5, bargein=False, survey=s )
        freecall.save()
        freecall_opt = Option(number="", action=OPTION_TRANSFER, prompt=freecall, action_param1=line.number)
        freecall_opt.save()
        
        return s
    else:
        return s[0]
    
def record_template(line, contenttype):
    prefix = line.dialstring_prefix
    suffix = line.dialstring_suffix
    language = line.language
    if line.outbound_number:
        num = line.outbound_number
    else:
        num = line.number
    
    name = contenttype[:3] +'_REC_' + broadcast.TEMPLATE_DESIGNATOR
    
    s = Survey.objects.filter(name=name)
    if not bool(s):
        s = Survey(name=name, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0, number=num, template=True)
        print ("adding template " + str(s))
        s.save()
    
        # welcome
        welcome = Prompt(file=language+"/welcome_bcast"+SOUND_EXT, order=1, bargein=True, survey=s, delay=0)
        welcome.save()
        welcome_opt = Option(number="", action=OPTION_NEXT, prompt=welcome)
        welcome_opt.save()
        welcome_opt2 = Option(number="1", action=OPTION_NEXT, prompt=welcome)
        welcome_opt2.save()
        
        # content
        content = Prompt(file=language+"/"+contenttype+SOUND_EXT, order=2, bargein=True, survey=s)
        content.save()
        content_opt = Option(number="", action=OPTION_NEXT, prompt=content)
        content_opt.save()
        content_opt2 = Option(number="1", action=OPTION_NEXT, prompt=content)
        content_opt2.save()
        
        # motivation
        motivation = Prompt(file=language+"/recordmotivation"+SOUND_EXT, order=4, bargein=True, survey=s, delay=0)
        motivation.save()
        motivation_opt = Option(number="", action=OPTION_NEXT, prompt=motivation)
        motivation_opt.save()
        motivation_opt2 = Option(number="1", action=OPTION_NEXT, prompt=motivation)
        motivation_opt2.save()
        
        # record
        record = Prompt(file=language+"/recordmessage"+SOUND_EXT, order=5, bargein=False, survey=s, name='Response' )
        record.save()
        record_opt = Option(number="", action=OPTION_RECORD, prompt=record, action_param2=7)
        record_opt.save()
        
        # thanks
        thanks = Prompt(file=language+"/recordthankyou"+SOUND_EXT, order=6, bargein=True, survey=s)
        thanks.save()
        thanks_opt = Option(number="", action=OPTION_NEXT, prompt=thanks)
        thanks_opt.save()
        
        return s
    else:
        return s[0]

def rating_template(line, contenttype, scheme, scales):
    prefix = line.dialstring_prefix
    suffix = line.dialstring_suffix
    language = line.language
    if line.outbound_number:
        num = line.outbound_number
    else:
        num = line.number
    
    name = contenttype[:3] + '_RATE_' + '_' + scheme + '_' + broadcast.TEMPLATE_DESIGNATOR
    
    s = Survey.objects.filter(name=name)
    if not bool(s):
        s = Survey(name=name, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0, number=num, template=True)
        print ("adding template " + str(s))
        s.save()
    
        # welcome
        welcome = Prompt(file=language+"/welcome_bcast"+SOUND_EXT, order=1, bargein=True, survey=s, delay=0)
        welcome.save()
        welcome_opt = Option(number="", action=OPTION_NEXT, prompt=welcome)
        welcome_opt.save()
        welcome_opt2 = Option(number="1", action=OPTION_NEXT, prompt=welcome)
        welcome_opt2.save()
        
        # content
        content = Prompt(file=language+"/"+contenttype+SOUND_EXT, order=2, bargein=True, survey=s)
        content.save()
        content_opt = Option(number="", action=OPTION_NEXT, prompt=content)
        content_opt.save()
        content_opt2 = Option(number="1", action=OPTION_NEXT, prompt=content)
        content_opt2.save()
        
        # motivation
        motivation = Prompt(file=language+"/ratemotivation"+SOUND_EXT, order=4, bargein=True, survey=s, delay=0)
        motivation.save()
        motivation_opt = Option(number="", action=OPTION_NEXT, prompt=motivation)
        motivation_opt.save()
        motivation_opt2 = Option(number="1", action=OPTION_NEXT, prompt=motivation)
        motivation_opt2.save()

        rate = Prompt(file=language+"/"+scheme+SOUND_EXT, order=5, bargein=True, delay=5000, survey=s, name='Rating')
        rate.save()
        idx = 1
        for scale in scales:
            scale_opt = Option(number=str(idx), action=OPTION_INPUT, prompt=rate)
            scale_opt.save()
            
        # add a noinput uption
        # exit without thanking
        noinput = Option(number="", action=OPTION_GOTO, action_param1=7, prompt=rate)
        noinput.save()
        
        
        # thanks
        thanks = Prompt(file=language+"/recordthankyou"+SOUND_EXT, order=6, bargein=True, survey=s)
        thanks.save()
        thanks_opt = Option(number="", action=OPTION_NEXT, prompt=thanks)
        thanks_opt.save()
        
        return s
    else:
        return s[0]

def main():
    line = Line.objects.get(pk=1)
    standard_template(line, 'qna')
    standard_template(line, 'announcement')
    standard_template(line, 'experience')
    
    freecall_template(line, 'qna')
    freecall_template(line, 'announcement')
    freecall_template(line, 'experience')
    
    record_template(line, 'qna')
    record_template(line, 'announcement')
    record_template(line, 'experience')
    
    scales = ["verygood", "good", "ok"]
    rating_template(line, "qna", "verygood", scales)
    rating_template(line, "announcement","verygood", scales)
    rating_template(line, "experience", "verygood", scales)
    
    scales = ["ok", "good", "verygood"]
    rating_template(line, "qna", "verygood_rev", scales)
    rating_template(line, "announcement", "verygood_rev", scales)
    rating_template(line, "experience", "verygood_rev", scales)
    
    scales = ["good", "ok", "bad"]
    rating_template(line, "qna","goodbad", scales)
    rating_template(line, "announcement", "goodbad", scales)
    rating_template(line, "experience", "goodbad", scales)
    
    scales = ["bad", "ok", "good"]
    rating_template(line, "qna", "badgood", scales)
    rating_template(line, "announcement", "badgood", scales)
    rating_template(line, "experience", "badgood", scales)
    
main()

