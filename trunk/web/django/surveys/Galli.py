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

# These should be consistent with the constants
# in survey.lua
OPTION_NEXT = 1
OPTION_PREV = 2
OPTION_REPLAY = 3
OPTION_GOTO = 4

SOUND_EXT = ".wav"

ACTIVITY_DURATION_DAYS = 2
ACTIVITY_START = timedelta(hours=11)
ACTIVITY_END = timedelta(hours=19)

CALL_BLOCK_SIZE = 10
# should match INTERVAL_MINS in survey.py and the frequency of the cron
CALL_BLOCK_INTERVAL_MINUTES = timedelta(minutes=10)

def subjects(numbers):
    count = 0
    subjs = []
    
    for number in numbers:
        if number != '':
            s = Subject.objects.filter(number = number)
            if not bool(s):
                s = Subject(number=str(number))
                print ("adding subject " + str(s))
                s.save()
                subjs.append(s)
                count += 1
            else:
                subjs.append(s[0])
            
    print(str(count) + " new subjects added.")
    print(str(len(subjs)) + " total subjects.")
    return subjs

def activity(activityfilename, line):
    prefix = line.dialstring_prefix
    suffix = line.dialstring_suffix
    language = line.language
    if line.outbound_number:
        num = line.outbound_number
    else:
        num = line.number
    
    name = line.name + '_' + activityfilename
    
    s = Survey.objects.filter(name=name)
    if not bool(s):
        s = Survey(name=name, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0, number=num)
        print ("adding activity of the week " + str(s))
        s.save()
    
        # welcome
        welcome = Prompt(file=language+"/welcome"+SOUND_EXT, order=1, bargein=False, survey=s)
        welcome.save()
        welcome_opt = Option(number="", action=OPTION_NEXT, prompt=welcome)
        welcome_opt.save()
        
        # activity
        a = Prompt(file=language+"/"+activityfilename+SOUND_EXT, order=2, bargein=False, survey=s)
        a.save()
        a_opt = Option(number="", action=OPTION_NEXT, prompt=a)
        a_opt.save()
        
        # thanks
        thanks = Prompt(file=language+"/signoff"+SOUND_EXT, order=3, bargein=True, delay=5000, survey=s)
        thanks.save()
        thanks_opt1 = Option(number="9", action=OPTION_GOTO, action_param1=2, prompt=thanks)
        thanks_opt1.save()
        thanks_opt2 = Option(number="", action=OPTION_NEXT, prompt=thanks)
        thanks_opt2.save()
        
        return s
    else:
        return s[0]  

def calls(activity, subjects, start_date):
    count = 0
    # This is the only survey to send, so the
    # block is the entire duration period
    survey_block_days = ACTIVITY_DURATION_DAYS
    
    survey_start_day = start_date
    assigned_p1s = []
    for survey_block_day in range(survey_block_days):
        survey_day = survey_start_day + timedelta(days=survey_block_day)
        call_time = survey_day + ACTIVITY_START
        
        if len(assigned_p1s) < len(subjects):
            pending_p1s = [subj for subj in subjects if subj not in assigned_p1s]
            i = 0
            while i < len(pending_p1s):
                subj_block = pending_p1s[i:i+CALL_BLOCK_SIZE]
                for subject in subj_block:
                    call = Call.objects.filter(survey=activity, subject=subject, priority=1)
                    if not bool(call):
                        call = Call(survey=activity, subject=subject, date=call_time, priority=1)
                        print ("adding call " + str(call))
                        call.save()
                        count += 1
                        assigned_p1s.append(subject)
                    
                i += CALL_BLOCK_SIZE
                call_time += CALL_BLOCK_INTERVAL_MINUTES
                
                if call_time > survey_day + ACTIVITY_END:
                    break
        
        # end P1 assignments
        # with any remaining time left, assign P2's
        backup_calls(activity, subjects, survey_day + ACTIVITY_START, survey_day + ACTIVITY_END)   

# keep adding, as many times as possible,
# backup phone calls in the given range
def backup_calls(survey, subjects, start_time, end_time):
    scheduled_calls = []
    count = 0
    call_time = start_time
    i = 0
    while i < len(subjects):
        scheduled_cnt = Call.objects.filter(date=call_time).count()
        if scheduled_cnt < CALL_BLOCK_SIZE:
            # get a block of numbers to call
            subj_block = subjects[i:i+CALL_BLOCK_SIZE]
            for subject in subj_block:
                call = Call.objects.filter(survey=survey, subject=subject, date=call_time, priority=2)
                if not bool(call):
                    call = Call(survey=survey, subject=subject, date=call_time, priority=2)
                    print ("adding call " + str(call))
                    call.save()
                    count += 1
                    scheduled_calls.append(subject)
            
            i += CALL_BLOCK_SIZE
            # keep adding the numbers over and over
            if i >= len(subjects):
                i = 0
                
        call_time += CALL_BLOCK_INTERVAL_MINUTES
        
        if call_time > end_time:
            break
    
    print(str(count) + " new backup calls added.")   
    
    return scheduled_calls

def standard_template(line, contenttype):
    prefix = line.dialstring_prefix
    suffix = line.dialstring_suffix
    language = line.language
    if line.outbound_number:
        number = line.outbound_number
    else:
        number = line.number
    
    name = contenttype[:3].upper()
    s = Survey.objects.filter(name=name, number=number, template=True)
    if bool(s):
        s = s[0]
        s.delete()
        print('deleting survey')
    s = Survey(name=name, number=number, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=1, template=True)
    s.save()
    print('creating new survey '+str(s))
    
    # welcome
    welcome = Prompt(file=language+"/welcome_"+contenttype[:3].upper()+SOUND_EXT, order=1, bargein=True, survey=s)
    welcome.save()
    welcome_opt1 = Option(number="", action=Option.NEXT, prompt=welcome)
    welcome_opt1.save()
    welcome_opt2 = Option(number="1", action=Option.NEXT, prompt=welcome)
    welcome_opt2.save()
    
    # content
#        content = Prompt(file=language+"/"+contenttype+SOUND_EXT, order=2, bargein=True, survey=s)
#        content.save()
#        content_opt = Option(number="", action=Option.NEXT, prompt=content)
#        content_opt.save()
#        content_opt2 = Option(number="1", action=Option.NEXT, prompt=content)
#        content_opt2.save()
    
    # thanks
    thanks = Prompt(file=language+"/thankyou_"+contenttype[:3].upper()+SOUND_EXT, order=3, bargein=True, survey=s)
    thanks.save()
    thanks_opt1 = Option(number="", action=Option.NEXT, prompt=thanks)
    thanks_opt1.save()
    thanks_opt2 = Option(number="9", action=Option.PREV, prompt=thanks)
    thanks_opt2.save()
        
    return s
    
def main():
    # get the forum
    '''
    if len(sys.argv) < 4:
        print("args: activityfilename, phonenumsfilename, lineid, <startdate>")
        sys.exit()
    else:
        activityfilename = sys.argv[1]
        numberfilename = sys.argv[2]
        lineid = sys.argv[3]
    
    now = datetime.now()
    today = datetime(year=now.year, month=now.month, day=now.day)
    tomorrow = today + timedelta(days=1)  
        
    if len(sys.argv) > 4:
        launch = datetime.strptime(sys.argv[4], "%m-%d-%Y")
    else:
        launch = tomorrow
        
    f = open(numberfilename)
    numbers = []
    while(True):
        num = f.readline()
        if not num:
            break
        numbers.append(num.strip())
        
    line = Line.objects.get(pk=int(lineid))
    
    subjs = subjects(numbers)
    act = activity(activityfilename, line)
    calls(act, subjs, launch)
    '''
    line = Line.objects.get(pk=2)
    #Survey.objects.filter(number__in=[line.number, line.outbound_number], template=True).delete()
    standard_template(line, 'aow')
    #standard_template(line, 'announcement')
    
main()

