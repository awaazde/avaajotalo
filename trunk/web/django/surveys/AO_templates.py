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
from otalo.ao.models import Line
from otalo.surveys.models import Survey, Subject, Call, Prompt, Option, Param
from random import shuffle

SOUND_EXT = ".wav"

def standard_template(line, contenttype):
    prefix = line.dialstring_prefix
    suffix = line.dialstring_suffix
    language = line.language
    if line.outbound_number:
        num = line.outbound_number
    else:
        num = line.number
    
    name = contenttype[:3].upper() + '_' + Survey.TEMPLATE_DESIGNATOR + ' (' + str(line.id) + ')'
    
    s = Survey.objects.filter(name=name)
    if not bool(s):
        s = Survey(name=name, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0, number=num, template=True)
        print ("adding template " + str(s))
        s.save()
    
        # welcome
        welcome = Prompt(file=language+"/welcome"+SOUND_EXT, order=1, bargein=True, survey=s)
        welcome.save()
        welcome_opt1 = Option(number="", action=Option.NEXT, prompt=welcome)
        welcome_opt1.save()
        welcome_opt2 = Option(number="1", action=Option.NEXT, prompt=welcome)
        welcome_opt2.save()
        
        # content
        content = Prompt(file=language+"/"+contenttype+SOUND_EXT, order=2, bargein=True, survey=s)
        content.save()
        content_opt = Option(number="", action=Option.NEXT, prompt=content)
        content_opt.save()
        content_opt2 = Option(number="1", action=Option.NEXT, prompt=content)
        content_opt2.save()
        
        # thanks
        thanks = Prompt(file=language+"/thankyou"+SOUND_EXT, order=4, bargein=True, delay=5000, survey=s)
        thanks.save()
        thanks_opt1 = Option(number="", action=Option.NEXT, prompt=thanks)
        thanks_opt1.save()
        thanks_opt2 = Option(number="1", action=Option.NEXT, prompt=thanks)
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
    
    name = contenttype[:3].upper() +'_CALL_' + Survey.TEMPLATE_DESIGNATOR
    
    s = Survey.objects.filter(name=name)
    if not bool(s):
        s = Survey(name=name, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0, number=num, template=True)
        print ("adding template " + str(s))
        s.save()
    
        # welcome
        welcome = Prompt(file=language+"/welcome_bcast"+SOUND_EXT, order=1, bargein=True, survey=s, delay=0)
        welcome.save()
        welcome_opt = Option(number="", action=Option.NEXT, prompt=welcome)
        welcome_opt.save()
        welcome_opt2 = Option(number="1", action=Option.NEXT, prompt=welcome)
        welcome_opt2.save()
        
        # content
        content = Prompt(file=language+"/"+contenttype+SOUND_EXT, order=2, bargein=True, survey=s)
        content.save()
        content_opt = Option(number="", action=Option.NEXT, prompt=content)
        content_opt.save()
        content_opt2 = Option(number="1", action=Option.NEXT, prompt=content)
        content_opt2.save()
        
        # motivation
        motivation = Prompt(file=language+"/recordmotivation"+SOUND_EXT, order=4, bargein=True, survey=s, delay=0)
        motivation.save()
        motivation_opt = Option(number="", action=Option.NEXT, prompt=motivation)
        motivation_opt.save()
        motivation_opt2 = Option(number="1", action=Option.NEXT, prompt=motivation)
        motivation_opt2.save()
        
        # freecall
        freecall = Prompt(file=language+"/freecall"+SOUND_EXT, order=5, bargein=True, survey=s )
        freecall.save()
        freecall_opt = Option(number="", action=Option.TRANSFER, prompt=freecall)
        freecall_opt.save()
        param1 = Param(option=freecall_opt, name=Param.NUM, value=line.number)
        param1.save()
        freecall_opt2 = Option(number="1", action=Option.TRANSFER, prompt=freecall)
        freecall_opt2.save()
        param2 = Param(option=freecall_opt2, name=Param.NUM, value=line.number)
        param2.save()
        
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
    
    name = contenttype[:3].upper() +'_REC_' + Survey.TEMPLATE_DESIGNATOR
    
    s = Survey.objects.filter(name=name)
    if not bool(s):
        s = Survey(name=name, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0, number=num, template=True)
        print ("adding template " + str(s))
        s.save()
    
        # welcome
        welcome = Prompt(file=language+"/welcome_bcast"+SOUND_EXT, order=1, bargein=True, survey=s, delay=0)
        welcome.save()
        welcome_opt = Option(number="", action=Option.NEXT, prompt=welcome)
        welcome_opt.save()
        welcome_opt2 = Option(number="1", action=Option.NEXT, prompt=welcome)
        welcome_opt2.save()
        
        # content
        content = Prompt(file=language+"/"+contenttype+SOUND_EXT, order=2, bargein=True, survey=s)
        content.save()
        content_opt = Option(number="", action=Option.NEXT, prompt=content)
        content_opt.save()
        content_opt2 = Option(number="1", action=Option.NEXT, prompt=content)
        content_opt2.save()
        
        # motivation
        motivation = Prompt(file=language+"/recordmotivation"+SOUND_EXT, order=4, bargein=True, survey=s, delay=0)
        motivation.save()
        motivation_opt = Option(number="", action=Option.NEXT, prompt=motivation)
        motivation_opt.save()
        motivation_opt2 = Option(number="1", action=Option.NEXT, prompt=motivation)
        motivation_opt2.save()
        
        # record
        record = Prompt(file=language+"/recordmessage"+SOUND_EXT, order=5, bargein=True, survey=s, name='Response' )
        record.save()
        record_opt = Option(number="", action=Option.RECORD, prompt=record)
        record_opt.save()
        param = Param(option=record_opt, name=Param.ONCANCEL, value=7)
        param.save()
        record_opt2 = Option(number="1", action=Option.RECORD, prompt=record)
        record_opt2.save()
        param2 = Param(option=record_opt2, name=Param.ONCANCEL, value=7)
        param2.save()
        
        # thanks
        thanks = Prompt(file=language+"/recordthankyou"+SOUND_EXT, order=6, bargein=True, survey=s)
        thanks.save()
        thanks_opt = Option(number="", action=Option.NEXT, prompt=thanks)
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
    
    name = contenttype[:3].upper() + '_RATE_' + '_' + scheme + '_' + Survey.TEMPLATE_DESIGNATOR
    
    s = Survey.objects.filter(name=name)
    if not bool(s):
        s = Survey(name=name, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0, number=num, template=True)
        print ("adding template " + str(s))
        s.save()
    
        # welcome
        welcome = Prompt(file=language+"/welcome_bcast"+SOUND_EXT, order=1, bargein=True, survey=s, delay=0)
        welcome.save()
        welcome_opt = Option(number="", action=Option.NEXT, prompt=welcome)
        welcome_opt.save()
        welcome_opt2 = Option(number="1", action=Option.NEXT, prompt=welcome)
        welcome_opt2.save()
        
        # content
        content = Prompt(file=language+"/"+contenttype+SOUND_EXT, order=2, bargein=True, survey=s)
        content.save()
        content_opt = Option(number="", action=Option.NEXT, prompt=content)
        content_opt.save()
        content_opt2 = Option(number="1", action=Option.NEXT, prompt=content)
        content_opt2.save()
        
        # motivation
        motivation = Prompt(file=language+"/ratemotivation"+SOUND_EXT, order=4, bargein=True, survey=s, delay=0)
        motivation.save()
        motivation_opt = Option(number="", action=Option.NEXT, prompt=motivation)
        motivation_opt.save()
        motivation_opt2 = Option(number="1", action=Option.NEXT, prompt=motivation)
        motivation_opt2.save()

        rate = Prompt(file=language+"/likert"+scheme+SOUND_EXT, order=5, bargein=True, delay=7000, survey=s, name='Rating')
        rate.save()
        idx = 1
        for scale in scales:
            scale_opt = Option(number=str(idx), action=Option.INPUT, prompt=rate)
            scale_opt.save()
            idx += 1
            
        # add a noinput uption
        # exit without thanking
        noinput = Option(number="", action=Option.GOTO, prompt=rate)
        noinput.save()
        param = Param(option=noinput, name=Param.IDX, value=7)
        param.save()
        
        
        # thanks
        thanks = Prompt(file=language+"/ratethankyou"+SOUND_EXT, order=6, bargein=True, survey=s)
        thanks.save()
        thanks_opt = Option(number="", action=Option.NEXT, prompt=thanks)
        thanks_opt.save()
        
        return s
    else:
        return s[0]

def main():
    line = Line.objects.get(pk=1)
    Survey.objects.filter(number__in=[line.number, line.outbound_number], template=True).delete()
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
    
    scales = ["good", "ok", "bad"]
    rating_template(line, "qna","goodbad", scales)
    rating_template(line, "announcement", "goodbad", scales)
    rating_template(line, "experience", "goodbad", scales)
    
main()

