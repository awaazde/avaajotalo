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
     

def motivation_template(line, contenttype, motivation):
    prefix = line.dialstring_prefix
    suffix = line.dialstring_suffix
    language = line.language
    if line.outbound_number:
        num = line.outbound_number
    else:
        num = line.number
    
    name = contenttype[:3].upper() +'_MOTIV_' + motivation.upper() + '_' + Survey.TEMPLATE_DESIGNATOR
    
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
        motivation = Prompt(file=language+"/recordmotivation"+motivation+SOUND_EXT, order=4, bargein=True, survey=s, delay=0)
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

def main():
    line = Line.objects.get(pk=2)
    Survey.objects.filter(number__in=[line.number, line.outbound_number], template=True).delete()
    standard_template(line, 'qna')
    standard_template(line, 'announcement')
    standard_template(line, 'experience')
    
    motivation_template(line, 'qna', 'none')
    motivation_template(line, 'announcement', 'none')
    motivation_template(line, 'experience', 'none')
    
    motivation_template(line, 'qna', 'self')
    motivation_template(line, 'announcement', 'self')
    motivation_template(line, 'experience', 'self')
    
    motivation_template(line, 'qna', 'group')
    motivation_template(line, 'announcement', 'group')
    motivation_template(line, 'experience', 'group')
    
    
main()

