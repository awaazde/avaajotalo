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

SOURCES = ["E1", "E2", "P1", "P2"]
MSGS = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"]
BEH_TYPES = ["BPRESS", "BCALL", "BHOLD"]

INBOUND = {"T1":"7930142001", "T2":"7930142002", "T3":"7930142003", "T4":"7930142004", "T5":"7930142005", "T6":"7930142006", "T7":"7930142007", "T8":"7930142008"}
EITHER = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22]
AM = [30,31,32,33]
PM = [34,35,36,37]
GROUPS = [["E1","P1","E2","P2","E2","P2","E1","P1"], ["E2","P2","E1","P1","E1","P1","E2","P2"], ["P1","E1","P2","E2","P2","E2","P1","E1"], ["P2","E2","P1","E1","P1","E1","P2","E2"]]
SUBJ_GROUPS = {}

AM_START = timedelta(hours=6)
AM_END = timedelta(hours=9)
PM_START = timedelta(hours=18)
PM_END = timedelta(hours=21)

# NOTE: surveys will be scheduled in order of their survey_id
#        if there are gaps in the ids, there will be a gap in the
#        time period between surveys
SURVEYS = ["T1_BCALL", "T2_BCALL", "T3_BCALL", "T4_BCALL", "T5_BCALL", "T6_BCALL", "T7_BCALL", "T8_BHOLD"]

STUDY_START = datetime(year=2010, month=8, day=1)
STUDY_DURATION_DAYS = 16

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
                    s = Survey(name=surname, dialstring_prefix=PREFIX, dialstring_suffix=SUFFIX)
                    print ("adding survey " + str(s))
                    s.save()
                    count = count + 1
    
    print(str(count) + " new surveys added")
    prompts()

def prompts():
    count = 0
    # iterate through all outbound surveys only
    for survey in Survey.objects.filter(number__isnull=True):
        # do this instead of prompt check in case there is a change
        # in the order or contents of prompts
        survey.prompt_set.all().delete()
        surveyname = survey.name
        
        # welcome
        welcome = Prompt(file="guj/welcome.wav", order=1, bargein=False, survey=survey)
        welcome.save()
        welcome_opt = Option(number="", action=OPTION_NEXT, prompt=welcome)
        welcome_opt.save()
        count = count + 1
        
        # tip
        tfilename = "guj/" + surveyname[:surveyname.index("_B")] + "_tip.wav"
        tip = Prompt(file=tfilename, order=2, bargein=False, survey=survey)
        tip.save()
        tip_opt = Option(number="", action=OPTION_NEXT, prompt=tip)
        tip_opt.save()
        count = count + 1

        # behavior
        bfilename = "guj/behavior.wav"
        behavior = Prompt(file=bfilename, order=3, bargein=False, delay=0, survey=survey)
        behavior.save()
        count = count + 1
        
        # Action step prompt
        btypeidx = surveyname.index('B')
        btype = surveyname[btypeidx+1:btypeidx+2]
        # special behavior for the press button for more info behavior
        if btype == 'P':
            action = Prompt(file="guj/press.wav", order=4, bargein=False, delay=0, survey=survey)
            action.save()
            
            repeat = Prompt(file="guj/repeat.wav", order=5, bargein=True, delay=5000, survey=survey)
            repeat.save()
            repeat_opt1 = Option(number="1", action=OPTION_NEXT, prompt=repeat)
            repeat_opt1.save()
            repeat_opt2 = Option(number="2", action=OPTION_GOTO, action_param1=2, prompt=repeat)
            repeat_opt2.save()
            survey.complete_after = 5
            
            # solution
            sfilename = "guj/" + surveyname[:surveyname.index("_B")] + "_solution.wav"
            solution = Prompt(file=sfilename, order=6, bargein=False, survey=survey)
            solution.save()
            soln_opt = Option(number="", action=OPTION_NEXT, prompt=solution)
            soln_opt.save()
            count = count + 1
            
            # followup
            followup = Prompt(file="guj/followup.wav", order=7, bargein=True, survey=survey)
            followup.save()
            followup_opt = Option(number="", action=OPTION_GOTO, action_param1=6, prompt=followup)
            followup_opt.save()
            count = count + 1
        elif btype == 'C':
            action = Prompt(file="guj/call.wav", order=4, bargein=False, delay=0, survey=survey)
            action.save()
            
            # phone num
            tipidx = surveyname.index('T')
            tip = surveyname[tipidx:surveyname.index('_',tipidx)]
            numfile = INBOUND[tip]
            phonenum = Prompt(file="guj/" + numfile + ".wav", order=5, bargein=False, delay=0, survey=survey)
            
            repeat = Prompt(file="guj/repeat.wav", order=6, bargein=True, delay=5000, survey=survey)
            repeat.save()
            repeat_opt1 = Option(number="2", action=OPTION_GOTO, action_param1=2, prompt=repeat)
            repeat_opt1.save()
            survey.complete_after = 6
        elif btype == 'H':
            survey.complete_after = 3
            # hold
            action = Prompt(file="guj/hold.wav", order=4, bargein=False, delay=0, survey=survey)
            action.save()
            action_opt1 = Option(number="2", action=OPTION_GOTO, action_param1=2, prompt=action)
            action_opt1.save()
            
            # solution
            sfilename = "guj/" + surveyname[:surveyname.index("_B")] + "_solution.wav"
            solution = Prompt(file=sfilename, order=5, bargein=False, survey=survey)
            solution.save()
            soln_opt = Option(number="", action=OPTION_NEXT, prompt=solution)
            soln_opt.save()
            count = count + 1
            
            # followup
            followup = Prompt(file="guj/followup.wav", order=6, bargein=True, survey=survey)
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
            number = INBOUND[msg]
            s = Survey.objects.filter(name=surname)
            if not bool(s):
                s = Survey(name=surname, dialstring_prefix=PREFIX, dialstring_suffix=SUFFIX, number=number)
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
        
        # solution
        sfilename = "guj/" + surveyname[:surveyname.index("_inbound")] + "_solution.wav"
        solution = Prompt(file=sfilename, order=1, bargein=False, survey=survey)
        solution.save()
        soln_opt = Option(number="", action=OPTION_NEXT, prompt=solution)
        soln_opt.save()
        count = count + 1
        
        # followup
        followup = Prompt(file="guj/followup.wav", order=2, bargein=True, survey=survey)
        followup.save()
        followup_opt = Option(number="", action=OPTION_PREV, prompt=followup)
        followup_opt.save()
        count = count + 1
        
    print(str(count) + " new inbound prompts added")   

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
def backup_calls(survey_label, nums, start_time, end_time):
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
                group_id = SUBJ_GROUPS[subject]
                messenger_label = GROUPS[group_id][SURVEYS.index(survey_label)]
                survey = Survey.objects.get(name__contains=messenger_label+'_'+survey_label)
                call = Call.objects.filter(survey=survey, subject=subject, date=call_time, priority=2)
                if not bool(call):
                    call = Call(survey=survey, subject=subject, date=call_time, priority=2)
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
    				
def main():
    subjects()
    surveys()
    inbound_surveys()
    calls()

main()
