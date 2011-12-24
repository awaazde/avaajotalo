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
import sys, csv
from datetime import datetime, timedelta
from otalo.AO.models import Line
from otalo.surveys.models import Survey, Subject, Call, Prompt, Option, Param
from random import shuffle

'''
****************************************************************************
******************* CONSTANTS **********************************************
****************************************************************************
'''
OUTPUT_FILE_DIR = ''
SOUND_EXT = ".wav"
BARGEIN_KEY='9'

'''
****************************************************************************
******************* SURVEY/TEMPLATE GENERATION *****************************
****************************************************************************
'''
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
        
        # repeat
        repeat = Prompt(file=language+"/repeat"+SOUND_EXT, order=4, bargein=True, delay=3000, survey=s)
        repeat.save()
        repeat_opt = Option(number="", action=Option.NEXT, prompt=repeat)
        repeat_opt.save()
        repeat_opt2 = Option(number="1", action=Option.NEXT, prompt=repeat)
        repeat_opt2.save()
        repeat_opt3 = Option(number="9", action=Option.GOTO, prompt=repeat)
        repeat_opt3.save()
        param = Param(option=repeat_opt2, name=Param.IDX, value=3)
        param.save()
        
        # thanks
        thanks = Prompt(file=language+"/thankyou"+SOUND_EXT, order=5, bargein=True, survey=s)
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
        welcome = Prompt(file=language+"/welcome"+SOUND_EXT, order=1, bargein=True, survey=s, delay=0)
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
        
         # repeat
        repeat = Prompt(file=language+"/repeat"+SOUND_EXT, order=4, bargein=True, delay=3000, survey=s)
        repeat.save()
        repeat_opt = Option(number="", action=Option.NEXT, prompt=repeat)
        repeat_opt.save()
        repeat_opt2 = Option(number="1", action=Option.NEXT, prompt=repeat)
        repeat_opt2.save()
        repeat_opt3 = Option(number="9", action=Option.GOTO, prompt=repeat)
        repeat_opt3.save()
        param = Param(option=repeat_opt3, name=Param.IDX, value=3)
        param.save()
               
        # freecall
        freecall = Prompt(file=language+"/freecall"+SOUND_EXT, order=5, bargein=True, delay=5000, survey=s )
        freecall.save()
        freecall_opt = Option(number="", action=Option.NEXT, prompt=freecall)
        freecall_opt.save()
        freecall_opt2 = Option(number="1", action=Option.TRANSFER, prompt=freecall)
        freecall_opt2.save()
        param = Param(option=freecall_opt2, name=Param.NUM, value=line.number)
        param.save()
        
        # thanks
        thanks = Prompt(file=language+"/thankyou"+SOUND_EXT, order=6, bargein=True, survey=s)
        thanks.save()
        thanks_opt1 = Option(number="", action=Option.NEXT, prompt=thanks)
        thanks_opt1.save()
        thanks_opt2 = Option(number="1", action=Option.NEXT, prompt=thanks)
        thanks_opt2.save()
        
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
        welcome = Prompt(file=language+"/welcome"+SOUND_EXT, order=1, bargein=True, survey=s, delay=0)
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
        
         # repeat
        repeat = Prompt(file=language+"/repeat"+SOUND_EXT, order=4, bargein=True, delay=3000, survey=s)
        repeat.save()
        repeat_opt = Option(number="", action=Option.NEXT, prompt=repeat)
        repeat_opt.save()
        repeat_opt2 = Option(number="1", action=Option.NEXT, prompt=repeat)
        repeat_opt2.save()
        repeat_opt3 = Option(number="9", action=Option.GOTO, prompt=repeat)
        repeat_opt3.save()
        param = Param(option=repeat_opt3, name=Param.IDX, value=3)
        param.save()
        
        # to record
        motivation = Prompt(file=language+"/recordmotivation"+SOUND_EXT, order=5, bargein=True, survey=s, delay=5000)
        motivation.save()
        motivation_opt = Option(number="", action=Option.GOTO, prompt=motivation)
        motivation_opt.save()
        param = Param(option=motivation_opt, name=Param.IDX, value=8)
        param.save()
        motivation_opt2 = Option(number="1", action=Option.NEXT, prompt=motivation)
        motivation_opt2.save()
        
        # record
        record = Prompt(file=language+"/recordmessage_short"+SOUND_EXT, order=6, bargein=True, survey=s, name='Response' )
        record.save()
        record_opt = Option(number="", action=Option.RECORD, prompt=record)
        record_opt.save()
        param = Param(option=record_opt, name=Param.ONCANCEL, value=8)
        param.save()
        record_opt2 = Option(number="1", action=Option.RECORD, prompt=record)
        record_opt2.save()
        param2 = Param(option=record_opt2, name=Param.ONCANCEL, value=8)
        param2.save()
        
        # thanks
        thanks = Prompt(file=language+"/recordthankyou"+SOUND_EXT, order=7, bargein=True, survey=s)
        thanks.save()
        thanks_opt = Option(number="", action=Option.GOTO, prompt=thanks)
        thanks_opt.save()
        param = Param(option=thanks_opt, name=Param.IDX, value=9)
        param.save()
        
        # thanks
        thanks = Prompt(file=language+"/thankyou"+SOUND_EXT, order=8, bargein=True, survey=s)
        thanks.save()
        thanks_opt1 = Option(number="", action=Option.NEXT, prompt=thanks)
        thanks_opt1.save()
        thanks_opt2 = Option(number="1", action=Option.NEXT, prompt=thanks)
        thanks_opt2.save()
        
        return s
    else:
        return s[0]
    
def subscription(line):
    prefix = line.dialstring_prefix
    suffix = line.dialstring_suffix
    language = line.language
    if line.outbound_number:
        num = line.outbound_number
    else:
        num = line.number
    
    name = 'Subscription_Survey_' + Survey.TEMPLATE_DESIGNATOR
    
    s = Survey.objects.filter(name=name)
    if bool(s):
        s = s[0]
        s.delete()
        
    s = Survey(name=name, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0, number=num, template=True)
    print ("adding template " + str(s))
    s.save()
    order = 1
    
    # welcome
    welcome = Prompt(file=language+"/welcome"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
    welcome.save()
    welcome_opt1 = Option(number="1", action=Option.NEXT, prompt=welcome)
    welcome_opt1.save()
    welcome_opt2 = Option(number="2", action=Option.GOTO, prompt=welcome)
    welcome_opt2.save()
    param = Param(option=welcome_opt2, name=Param.IDX, value=7)
    param.save()
    order += 1
    
    oksubscribe = Prompt(file=language+"/oksubscribe"+SOUND_EXT, order=order, bargein=True, survey=s, delay=0)
    oksubscribe.save()
    oksubscribe_opt1 = Option(number="", action=Option.NEXT, prompt=oksubscribe)
    oksubscribe_opt1.save()
    oksubscribe_opt2 = Option(number=BARGEIN_KEY, action=Option.NEXT, prompt=oksubscribe)
    oksubscribe_opt2.save()
    order += 1
    
    buysell = Prompt(file=language+"/buysell"+SOUND_EXT, order=order, bargein=True, survey=s, delay=3000)
    buysell.save()
    buysell_opt1 = Option(number="1", action=Option.INPUT, prompt=buysell)
    buysell_opt1.save()
    buysell_opt2 = Option(number="2", action=Option.INPUT, prompt=buysell)
    buysell_opt2.save()
    order += 1
    
    sksystem = Prompt(file=language+"/sksystem"+SOUND_EXT, order=order, bargein=True, survey=s, delay=3000)
    sksystem.save()
    sksystem_opt1 = Option(number="1", action=Option.INPUT, prompt=sksystem)
    sksystem_opt1.save()
    sksystem_opt2 = Option(number="2", action=Option.INPUT, prompt=sksystem)
    sksystem_opt2.save()
    order += 1
    
    jaherat = Prompt(file=language+"/jaherat"+SOUND_EXT, order=order, bargein=True, survey=s, delay=3000)
    jaherat.save()
    jaherat_opt1 = Option(number="1", action=Option.INPUT, prompt=jaherat)
    jaherat_opt1.save()
    jaherat_opt2 = Option(number="2", action=Option.INPUT, prompt=jaherat)
    jaherat_opt2.save()
    order += 1
    
    thankyou = Prompt(file=language+"/thankyou"+SOUND_EXT, order=order, bargein=False, survey=s, delay=0)
    thankyou.save()
    thankyou_opt1 = Option(number="", action=Option.GOTO, prompt=thankyou)
    thankyou_opt1.save()
    param = Param(option=thankyou_opt1, name=Param.IDX, value=order+3)
    param.save()
    order += 1
    
    # unsubscribe
    unsubscribe_dummy = Prompt(file=language+"/blank"+SOUND_EXT, order=order, bargein=False, survey=s, delay=0)
    unsubscribe_dummy.save()
    unsubscribe_dummy_opt1 = Option(number="", action=Option.INPUT, prompt=unsubscribe_dummy)
    unsubscribe_dummy_opt1.save()
    order += 1
    
    unsubscribe = Prompt(file=language+"/unsubscribe"+SOUND_EXT, order=order, bargein=False, survey=s, delay=0)
    unsubscribe.save()
    unsubscribe_opt1 = Option(number="", action=Option.NEXT, prompt=unsubscribe)
    unsubscribe_opt1.save()
    order += 1

    return s

'''
****************************************************************************
******************* Reporting **********************************************
****************************************************************************
'''
def subscription_results(line, date_start=False, date_end=False): 
    calls = Call.objects.filter(survey__number=line.number, survey__name__contains='Subscription_Survey_', complete=True)
    
    if date_start:
        calls = calls.filter(date__gte=date_start)
        
    if date_end:
        calls = calls.filter(date__lt=date_end)
    
    header = ['CallerNum', 'time', 'buysell', 'sksystem', 'jaherat', 'blank']
    results = [header]
    for call in calls:
        inputs = Input.objects.select_related(depth=1).filter(call=call)
        inputtbl = {}
        for input in inputs:
            file = input.prompt.file
            key = file[file.rfind('/')+1:file.find(SOUND_EXT)]
            inputtbl[key] = input.input
        result = [str(call.id), call.subject.number, time_str(call.date)]
        for prompt in header[2:]:
            if prompt in inputtbl:
                result.append(inputtbl[prompt])
            else:
                result.apppend('')
        results.append(result)
    
    if date_start:
        outfilename='sks_survey_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]+'.csv'
    else:
        outfilename='sks_survey.csv'
        
    outfilename = OUTPUT_FILE_DIR+outfilename
    output = csv.writer(open(outfilename, 'wb'))
    output.writerows(results)
    
def main():
    line = Line.objects.get(pk=3)
    #Survey.objects.filter(number__in=[line.number, line.outbound_number], template=True).delete()
    
    #freecall_template(line, 'announcement')
    #record_template(line, 'announcement')
    #freecall_template(line, 'qna')
    #record_template(line, 'qna')
    #subscription(line)
    subscription_results(line)
        
main()

