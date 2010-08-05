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
from datetime import datetime, timedelta
from otalo.surveys.models import Survey, Subject, Call, Prompt, Option
from random import shuffle

# These should be consistent with the constants
# in survey.lua
OPTION_NEXT = 1
OPTION_PREV = 2
OPTION_REPLAY = 3
OPTION_GOTO = 4

PREFIX = "openzap/smg_prid/a/"
SUFFIX = "@g2"
SOUND_EXT = ".mp3"
REMINDER_NAME = "REMINDER"

SOURCES = ["E1", "E2", "P1", "P2"]
MSGS = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"]
BEH_TYPES = ["BPRESS", "BCALL", "BHOLD"]

INBOUND_PREFIX = "793014"
INBOUND_SUFFIX_START = 2001
INBOUND = {}
EITHER = [9979403085,9879677274,9979254830,9924057403,9879417564,9558576090,9824387276,9727304678,9727281248,9726488991,9725317885,9723202471,9714174065,9712410421,9624235420,9510748795,9429260174,9429122745,9428897286,9428485487,9428459215,9427258722,9427037241,8140128125,9998750661,9979780231]
AM = []
PM = [9978171686, 9913461992]
GROUPS = [["E1","E2","P1","P2","E1","P1","E2","P2"], ["E2","E1","P2","P1","E2","P2","E1","P1"], ["P1","P2","E1","E2","P1","E1","P2","E2"], ["P2","P1","E2","E1","P2","E2","P1","E1"]]
SUBJ_GROUPS = {}

AM_START = timedelta(hours=6)
AM_END = timedelta(hours=9)
PM_START = timedelta(hours=18)
PM_END = timedelta(hours=21)

# NOTE: surveys will be scheduled in order of their survey_id
#        if there are gaps in the ids, there will be a gap in the
#        time period between surveys
SURVEYS = ["T1_BCALL", "T2_BCALL", "T3_BCALL", "T4_BCALL", "T5_BCALL", "T6_BCALL", "T7_BCALL", "T8_BHOLD"]

STUDY_START = datetime(year=2010, month=7, day=31)
STUDY_DURATION_DAYS = 16

REMINDER_START_DATE = datetime(year=2010, month=7, day=30)
REMINDER_DURATION_DAYS = 1
REMINDER_START = timedelta(hours=8)
REMINDER_END = timedelta(hours=18)

CALL_BLOCK_SIZE = 10
# should match INTERVAL_MINS in survey.py and the frequency of the cron
CALL_BLOCK_INTERVAL_MINUTES = timedelta(minutes=10)

def subjects():
    count = 0
    group_assignment = 0;
    
    all = EITHER + AM + PM
    for number in all:
        s = Subject.objects.filter(number = number)
        if not bool(s):
            s = Subject(number=str(number))
            print ("adding subject " + str(s))
            s.save()
            count += 1
    
    print(str(count) + " new subjects added.")
    
def surveys():    
    count = 0
    for source in SOURCES:
        for msg in MSGS:
            for btype in BEH_TYPES:
                surname = source + "_" + msg + "_" + btype
                s = Survey.objects.filter(name=surname)
                if not bool(s):
                    s = Survey(name=surname, dialstring_prefix=PREFIX, dialstring_suffix=SUFFIX, complete_after=2)
                    print ("adding survey " + str(s))
                    s.save()
                    count = count + 1
    
    print(str(count) + " new surveys added")
    prompts()

def prompts():
    count = 0
    
    surveys = []
    for surname in SURVEYS:
        surveys += Survey.objects.filter(name__contains=surname)
            
    # iterate through all outbound surveys only
    for survey in surveys:
        # do this instead of prompt check in case there is a change
        # in the order or contents of prompts
        survey.prompt_set.all().delete()
        surveyname = survey.name
        
        # welcome
        welcome = Prompt(file="guj/welcome" + SOUND_EXT, order=1, bargein=False, survey=survey)
        welcome.save()
        welcome_opt = Option(number="", action=OPTION_NEXT, prompt=welcome)
        welcome_opt.save()
        count = count + 1
        
        # tip
        tfilename = "guj/" + surveyname[:surveyname.index("_B")] + "_tip" + SOUND_EXT
        tip = Prompt(file=tfilename, order=2, bargein=False, delay=0, survey=survey)
        tip.save()
        tip_opt = Option(number="", action=OPTION_NEXT, prompt=tip)
        tip_opt.save()
        count = count + 1

        # behavior
        bfilename = "guj/behavior" + SOUND_EXT
        behavior = Prompt(file=bfilename, order=3, bargein=False, delay=0, survey=survey)
        behavior.save()
        beh_opt = Option(number="", action=OPTION_NEXT, prompt=behavior)
        beh_opt.save()
        count = count + 1
        
        # Action step prompt
        btypeidx = surveyname.index('B')
        btype = surveyname[btypeidx+1:btypeidx+2]
        # special behavior for the press button for more info behavior
        if btype == 'P':
            action = Prompt(file="guj/press" + SOUND_EXT, order=4, bargein=False, delay=0, survey=survey)
            action.save()
            action_opt = Option(number="", action=OPTION_NEXT, prompt=action)
            action_opt.save()
            
            repeat = Prompt(file="guj/repeat" + SOUND_EXT, order=5, bargein=True, delay=2000, survey=survey)
            repeat.save()
            repeat_opt1 = Option(number="1", action=OPTION_NEXT, prompt=repeat)
            repeat_opt1.save()
            repeat_opt2 = Option(number="2", action=OPTION_GOTO, action_param1=2, prompt=repeat)
            repeat_opt2.save()
            
            # solution confirm
            oksolution = Prompt(file="guj/oksolution" + SOUND_EXT, order=6, bargein=False, survey=survey)
            oksolution.save()
            oksoln_opt = Option(number="", action=OPTION_NEXT, prompt=oksolution)
            oksoln_opt.save()
            count = count + 1
            
            # solution
            sfilename = "guj/" + surveyname[:surveyname.index("_B")] + "_solution" + SOUND_EXT
            solution = Prompt(file=sfilename, order=7, bargein=False, survey=survey)
            solution.save()
            soln_opt = Option(number="", action=OPTION_NEXT, prompt=solution)
            soln_opt.save()
            count = count + 1
            
            # followup
            followup = Prompt(file="guj/followup" + SOUND_EXT, order=8, bargein=True, survey=survey)
            followup.save()
            followup_opt = Option(number="", action=OPTION_GOTO, action_param1=6, prompt=followup)
            followup_opt.save()
            count = count + 1
        elif btype == 'C':
            action = Prompt(file="guj/call" + SOUND_EXT, order=4, bargein=False, delay=0, survey=survey)
            action.save()
            action_opt = Option(number="", action=OPTION_NEXT, prompt=action)
            action_opt.save()
            
            # phone num
            tipidx = surveyname.index('T')
            tip = surveyname[:surveyname.index('_',tipidx)]
            numfile = INBOUND[tip]
            phonenum = Prompt(file="guj/" + numfile + SOUND_EXT, order=5, bargein=False, delay=0, survey=survey)
            phonenum.save()
            phonenum_opt = Option(number="", action=OPTION_NEXT, prompt=phonenum)
            phonenum_opt.save()
            
            repeat = Prompt(file="guj/repeat" + SOUND_EXT, order=6, bargein=True, delay=1000, survey=survey)
            repeat.save()
            repeat_opt1 = Option(number="", action=OPTION_GOTO, action_param1=3, prompt=repeat)
            repeat_opt1.save()
            repeat_opt2 = Option(number="2", action=OPTION_GOTO, action_param1=2, prompt=repeat)
            repeat_opt2.save()
        elif btype == 'H':
            # hold
            action = Prompt(file="guj/hold" + SOUND_EXT, order=4, bargein=False, delay=0, survey=survey)
            action.save()
            action_opt1 = Option(number="", action=OPTION_NEXT, prompt=action)
            action_opt1.save()
            action_opt2 = Option(number="2", action=OPTION_GOTO, action_param1=2, prompt=action)
            action_opt2.save()
            
            # solution
            sfilename = "guj/" + surveyname[:surveyname.index("_B")] + "_solution" + SOUND_EXT
            solution = Prompt(file=sfilename, order=5, bargein=False, survey=survey)
            solution.save()
            soln_opt = Option(number="", action=OPTION_NEXT, prompt=solution)
            soln_opt.save()
            count = count + 1
            
            # followup
            followup = Prompt(file="guj/followup" + SOUND_EXT, order=6, bargein=True, survey=survey)
            followup.save()
            followup_opt = Option(number="", action=OPTION_GOTO, action_param1=5, prompt=followup)
            followup_opt.save()
            count = count + 1
                        
    print(str(count) + " new prompts added")
    
def inbound_surveys():
    count = 0
    for source in SOURCES:
        for msg in MSGS:
            surname = source + "_" + msg + "_inbound"
            number = INBOUND[source + "_" + msg]
            s = Survey.objects.filter(name=surname)
            if not bool(s):
                s = Survey(name=surname, dialstring_prefix=PREFIX, dialstring_suffix=SUFFIX, number=number, complete_after=1)
                print ("adding inbound survey " + str(s))
                s.save()
                count = count + 1
    
    print(str(count) + " new inbound surveys added")
    inbound_prompts()
    
def inbound_prompts():
    count = 0
    # iterate through all inbound surveys only
    for survey in Survey.objects.filter(number__isnull=False):
        # do this instead of prompt check in case there is a change
        # in the order or contents of prompts
        survey.prompt_set.all().delete()
        surveyname = survey.name
        
        # solution confirm
        oksolution = Prompt(file="guj/oksolution" + SOUND_EXT, order=1, bargein=False, survey=survey)
        oksolution.save()
        oksoln_opt = Option(number="", action=OPTION_NEXT, prompt=oksolution)
        oksoln_opt.save()
        count = count + 1
        
        # solution
        sfilename = "guj/" + surveyname[:surveyname.index("_inbound")] + "_solution" + SOUND_EXT
        solution = Prompt(file=sfilename, order=2, bargein=False, survey=survey)
        solution.save()
        soln_opt = Option(number="", action=OPTION_NEXT, prompt=solution)
        soln_opt.save()
        count = count + 1
        
        # followup
        followup = Prompt(file="guj/followup" + SOUND_EXT, order=3, bargein=True, survey=survey)
        followup.save()
        followup_opt = Option(number="", action=OPTION_PREV, prompt=followup)
        followup_opt.save()
        count = count + 1
        
    print(str(count) + " new inbound prompts added")   

def reminder_survey():
    count = 0

    s = Survey.objects.filter(name=REMINDER_NAME)
    if not bool(s):
        s = Survey(name=REMINDER_NAME, dialstring_prefix=PREFIX, dialstring_suffix=SUFFIX, complete_after=1)
        print ("adding reminder survey " + str(s))
        s.save()
        
        reminder_prompt = Prompt(file="guj/reminder" + SOUND_EXT, order=1, bargein=False, delay=0, survey=s)
        reminder_prompt.save()
        count = count + 1
    
    print(str(count) + " new reminder survey added")
    
def reminder_calls():
    count = 0
    reminder_survey = Survey.objects.get(name=REMINDER_NAME)
    # This is the only survey to send, so the
    # block is the entire duration period
    survey_block_days = REMINDER_DURATION_DAYS
    
    all_nums = AM + EITHER + PM
    
    survey_start_day = REMINDER_START_DATE
    assigned_p1s = []
    for survey_block_day in range(survey_block_days):
        survey_day = survey_start_day + timedelta(days=survey_block_day)
        call_time = survey_day + REMINDER_START
        
        if len(assigned_p1s) < len(all_nums):
            pending_p1s = [num for num in all_nums if num not in assigned_p1s]
            i = 0
            while i < len(pending_p1s):
                num_block = pending_p1s[i:i+CALL_BLOCK_SIZE]
                for num in num_block:
                    subject = Subject.objects.get(number=str(num))
                    call = Call.objects.filter(survey=reminder_survey, subject=subject, priority=1)
                    if not bool(call):
                        call = Call(survey=reminder_survey, subject=subject, date=call_time, priority=1)
                        print ("adding reminder call " + str(call))
                        call.save()
                        count += 1
                        assigned_p1s.append(num)
                    
                i += CALL_BLOCK_SIZE
                call_time += CALL_BLOCK_INTERVAL_MINUTES
                
                if call_time > survey_day + REMINDER_END:
                    break
        
        # end P1 assignments
        # with any remaining time left, assign P2's
        backup_calls("", all_nums, survey_day + REMINDER_START, survey_day + REMINDER_END, survey=reminder_survey)   

def calls():
    count = 0
    survey_block_days = STUDY_DURATION_DAYS / len(SURVEYS)
    
    all_nums = AM + EITHER + PM
    
    # randomly assign groups to subjects
    group_assignment = 0
    for num in all_nums:
        s = Subject.objects.get(number=str(num))
        SUBJ_GROUPS[s] = group_assignment
        group_assignment += 1
        if group_assignment == len(GROUPS):
            group_assignment = 0

    for survey_label in SURVEYS:
        assigned_p1s = []
        
        # surveys are spread out evenly over the study period.
        # IMPORTANT ASSUMPTIONS: 
        #    1. There is at least one day for each survey
        #    2. Within each survey period there is enough time to schedule P1s for
        #       every number given the CALL_BLOCK_SIZE and the CALL_BLOCK_INTERVAL
        survey_start_day = STUDY_START + timedelta(days=survey_block_days) * SURVEYS.index(survey_label)
        
        for survey_block_day in range(survey_block_days):
            survey_day = survey_start_day + timedelta(days=survey_block_day)
            call_time = survey_day + AM_START
            
            if len(assigned_p1s) < len(all_nums):
                # there are still some P1 calls to assign
                
                # AM
                pending_AM_p1s = [num for num in AM if num not in assigned_p1s]
                i = 0
                while i < len(pending_AM_p1s):
                    # get a block of numbers to call
                    num_block = pending_AM_p1s[i:i+CALL_BLOCK_SIZE]
                    for num in num_block:
                        subject = Subject.objects.get(number=str(num))
                        group_id = SUBJ_GROUPS[subject]
                        messenger_label = GROUPS[group_id][SURVEYS.index(survey_label)]
                        #print "looking for survey " + messenger_label+'_'+survey_label
                        survey = Survey.objects.get(name__contains=messenger_label+'_'+survey_label)
                        call = Call.objects.filter(survey=survey, subject=subject, priority=1)
                        if not bool(call):
                            call = Call(survey=survey, subject=subject, date=call_time, priority=1)
                            print ("adding call " + str(call))
                            call.save()
                            count += 1
                            assigned_p1s.append(num)
                        
                    i += CALL_BLOCK_SIZE
                    call_time += CALL_BLOCK_INTERVAL_MINUTES
                    
                    if call_time > survey_day + AM_END:
                        break
                    
                if call_time <= survey_day + AM_END:
                    # start assigning EITHER calls from where we left off above
                    pending_EITHER_p1s = [num for num in EITHER if num not in assigned_p1s]
                    i = 0
                    while i < len(pending_EITHER_p1s):
                        # get a block of numbers to call
                        num_block = pending_EITHER_p1s[i:i+CALL_BLOCK_SIZE]
                        for num in num_block:
                            subject = Subject.objects.get(number=str(num))
                            group_id = SUBJ_GROUPS[subject]
                            messenger_label = GROUPS[group_id][SURVEYS.index(survey_label)]
                            survey = Survey.objects.get(name__contains=messenger_label+'_'+survey_label)
                            call = Call.objects.filter(survey=survey, subject=subject, priority=1)
                            if not bool(call):
                                call = Call(survey=survey, subject=subject, date=call_time, priority=1)
                                print ("adding call " + str(call))
                                call.save()
                                count += 1
                                assigned_p1s.append(num)
                            
                        i += CALL_BLOCK_SIZE
                        call_time += CALL_BLOCK_INTERVAL_MINUTES
                        
                        if call_time > survey_day + AM_END:
                            break
                        
                #PM
                call_time = survey_day + PM_START
                pending_PM_p1s = [num for num in PM if num not in assigned_p1s]
                i = 0
                while i < len(pending_PM_p1s):
                    # get a block of numbers to call
                    num_block = pending_PM_p1s[i:i+CALL_BLOCK_SIZE]
                    for num in num_block:
                        subject = Subject.objects.get(number=str(num))
                        group_id = SUBJ_GROUPS[subject]
                        messenger_label = GROUPS[group_id][SURVEYS.index(survey_label)]
                        survey = Survey.objects.get(name__contains=messenger_label+'_'+survey_label)
                        call = Call.objects.filter(survey=survey, subject=subject, priority=1)
                        if not bool(call):
                            call = Call(survey=survey, subject=subject, date=call_time, priority=1)
                            print ("adding call " + str(call))
                            call.save()
                            count += 1
                            assigned_p1s.append(num)
                        
                    i += CALL_BLOCK_SIZE
                    call_time += CALL_BLOCK_INTERVAL_MINUTES
                    
                    if call_time > survey_day + PM_END:
                        break
                    
                if call_time <= survey_day + PM_END:  
                    # start assigning EITHER calls from where we left off above
                    pending_EITHER_p1s = [num for num in EITHER if num not in assigned_p1s]
                    i = 0
                    while i < len(pending_EITHER_p1s):
                        # get a block of numbers to call
                        num_block = pending_EITHER_p1s[i:i+CALL_BLOCK_SIZE]
                        for num in num_block:
                            subject = Subject.objects.get(number=str(num))
                            group_id = SUBJ_GROUPS[subject]
                            messenger_label = GROUPS[group_id][SURVEYS.index(survey_label)]
                            survey = Survey.objects.get(name__contains=messenger_label+'_'+survey_label)
                            call = Call.objects.filter(survey=survey, subject=subject, priority=1)
                            if not bool(call):
                                call = Call(survey=survey, subject=subject, date=call_time, priority=1)
                                print ("adding call " + str(call))
                                call.save()
                                count += 1
                                assigned_p1s.append(num)
                            
                        i += CALL_BLOCK_SIZE
                        call_time += CALL_BLOCK_INTERVAL_MINUTES
                        
                        if call_time > survey_day + PM_END:
                            break
            # end P1 assignments
            # with any remaining time left, assign P2's
            backup_calls(survey_label, AM+EITHER, survey_day + AM_START, survey_day + AM_END)
            backup_calls(survey_label, PM+EITHER, survey_day + PM_START, survey_day + PM_END)
                    
    print(str(count) + " new calls added.")            

# keep adding, as many times as possible,
# backup phone calls in the given range
def backup_calls(survey_label, nums, start_time, end_time, survey=False):
    scheduled_calls = []
    count = 0
    call_time = start_time
    i = 0
    while i < len(nums):
        scheduled_cnt = Call.objects.filter(date=call_time).count()
        if scheduled_cnt == 0:
            # get a block of numbers to call
            num_block = nums[i:i+CALL_BLOCK_SIZE]
            for num in num_block:
                subject = Subject.objects.get(number=str(num))
                if not survey:
                    group_id = SUBJ_GROUPS[subject]
                    messenger_label = GROUPS[group_id][SURVEYS.index(survey_label)]
                    s = Survey.objects.get(name__contains=messenger_label+'_'+survey_label)
                else:
                    s = survey
                call = Call.objects.filter(survey=s, subject=subject, date=call_time, priority=2)
                if not bool(call):
                    call = Call(survey=s, subject=subject, date=call_time, priority=2)
                    print ("adding call " + str(call))
                    call.save()
                    count += 1
                    scheduled_calls.append(num)
            
            i += CALL_BLOCK_SIZE
            # keep adding the numbers over and over
            if i >= len(nums):
                i = 0
                
        call_time += CALL_BLOCK_INTERVAL_MINUTES
        
        if call_time > end_time:
            break
    
    print(str(count) + " new backup calls added.")   
    
    return scheduled_calls

def shift_calls(starting, timeshift):
    calls = Call.objects.filter(date__gte=starting)
    
    for call in calls:
        print ("shifting " + str(call) + " to date " + str(call.date + timeshift))
        call.date += timeshift
        call.save()
                 
def main():
    # create inbound number assignments
    suffix = INBOUND_SUFFIX_START
    for source in SOURCES:
        for msg in MSGS:
            surname = source + "_" + msg
            INBOUND[surname] = INBOUND_PREFIX + str(suffix)
            suffix += 1
            
    subjects()
    surveys()
    calls()
    inbound_surveys()
    reminder_survey()
    reminder_calls()
    
    shift_start = datetime(year=2010, month=8, day=2)
    oneday = timedelta(days=1)
    #shift_calls(shift_start, oneday)

main()

