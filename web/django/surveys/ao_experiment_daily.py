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
"""
PURPOSE OF THIS SCRIPT:

Run once a day before the study's calls are scheduled to begin.
Will schedule calls based on previously completed surveys up to that point

Based on the number of surveys and the study period, it will schedule the survey
that should be run if the surveys were spread out evenly over the study period.

It can be run more than once a day safely, though it's not meant for that.
"""
import sys
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
EITHER = [1,2,3,4,5]
AM = [6,7,8]
PM = [9,10,11,12,13,9913461992]
GROUPS = [["REMINDER_DUMMY","E1","E2","P1","P2","E1","P1","E2","P2"], ["REMINDER_DUMMY","E2","E1","P2","P1","E2","P2","E1","P1"], ["REMINDER_DUMMY","P1","P2","E1","E2","P1","E1","P2","E2"], ["REMINDER_DUMMY","P2","P1","E2","E1","P2","E2","P1","E1"]]

AM_START = timedelta(hours=6)
AM_END = timedelta(hours=9)
PM_START = timedelta(hours=18)
PM_END = timedelta(hours=21)

# The actual surveys to run, in the order to run them in
SURVEYS = ["REMINDER", "T1_BPRESS", "T2_BCALL", "T3_BPRESS", "T4_BPRESS", "T5_BPRESS", "T6_BPRESS", "T7_BPRESS", "T8_BHOLD"]

STUDY_START = datetime(year=2010, month=8, day=14)
STUDY_DURATION_DAYS = 18

REMINDER_START = timedelta(hours=8)
REMINDER_END = timedelta(hours=18)

CALL_BLOCK_SIZE = 10
# should match INTERVAL_MINS in survey.py and the frequency of the cron
CALL_BLOCK_INTERVAL_MINUTES = timedelta(minutes=10)   

def calls(days_from_start):
    count = 0
    survey_block_days = STUDY_DURATION_DAYS / len(SURVEYS)
    
    # find out which survey to run today
    survey_label = SURVEYS[days_from_start/survey_block_days]
    
    if survey_label == REMINDER_NAME:
        return reminder_calls(days_from_start)
    
    all_nums = AM + EITHER + PM
    
    survey_day = STUDY_START + timedelta(days=days_from_start)
    call_time = survey_day + AM_START
    
    subjs_completed = Subject.objects.filter(call__survey__name__contains=survey_label, call__date__lt=survey_day, call__complete=True)
    completed = [int(subj.number) for subj in subjs_completed]
    
    pending_p1s = [num for num in all_nums if num not in completed]
    if pending_p1s:
        # there are still some P1 calls to assign
        
        # AM
        pending_AM_p1s = [num for num in AM if num not in completed]
        i = 0
        while i < len(pending_AM_p1s):
            # get a block of numbers to call
            num_block = pending_AM_p1s[i:i+CALL_BLOCK_SIZE]
            for num in num_block:
                subject = Subject.objects.get(number=str(num))
                messenger_label = GROUPS[subject.group][SURVEYS.index(survey_label)]
                #print "looking for survey " + messenger_label+'_'+survey_label
                survey = Survey.objects.get(name__contains=messenger_label+'_'+survey_label)
                call = Call.objects.filter(survey=survey, subject=subject, date__gte=survey_day, priority=1)
                if not bool(call):
                    call = Call(survey=survey, subject=subject, date=call_time, priority=1)
                    print ("adding call " + str(call))
                    call.save()
                    count += 1
                    completed.append(num)
                
            i += CALL_BLOCK_SIZE
            call_time += CALL_BLOCK_INTERVAL_MINUTES
            
            if call_time > survey_day + AM_END:
                break
            
        if call_time <= survey_day + AM_END:
            # start assigning EITHER calls from where we left off above
            pending_EITHER_p1s = [num for num in EITHER if num not in completed]
            i = 0
            while i < len(pending_EITHER_p1s):
                # get a block of numbers to call
                num_block = pending_EITHER_p1s[i:i+CALL_BLOCK_SIZE]
                for num in num_block:
                    subject = Subject.objects.get(number=str(num))
                    messenger_label = GROUPS[subject.group][SURVEYS.index(survey_label)]
                    survey = Survey.objects.get(name__contains=messenger_label+'_'+survey_label)
                    call = Call.objects.filter(survey=survey, subject=subject, date__gte=survey_day, priority=1)
                    if not bool(call):
                        call = Call(survey=survey, subject=subject, date=call_time, priority=1)
                        print ("adding call " + str(call))
                        call.save()
                        count += 1
                        completed.append(num)
                    
                i += CALL_BLOCK_SIZE
                call_time += CALL_BLOCK_INTERVAL_MINUTES
                
                if call_time > survey_day + AM_END:
                    break
                
        #PM
        call_time = survey_day + PM_START
        pending_PM_p1s = [num for num in PM if num not in completed]
        i = 0
        while i < len(pending_PM_p1s):
            # get a block of numbers to call
            num_block = pending_PM_p1s[i:i+CALL_BLOCK_SIZE]
            for num in num_block:
                subject = Subject.objects.get(number=str(num))
                messenger_label = GROUPS[subject.group][SURVEYS.index(survey_label)]
                survey = Survey.objects.get(name__contains=messenger_label+'_'+survey_label)
                call = Call.objects.filter(survey=survey, subject=subject, date__gte=survey_day, priority=1)
                if not bool(call):
                    call = Call(survey=survey, subject=subject, date=call_time, priority=1)
                    print ("adding call " + str(call))
                    call.save()
                    count += 1
                    completed.append(num)
                
            i += CALL_BLOCK_SIZE
            call_time += CALL_BLOCK_INTERVAL_MINUTES
            
            if call_time > survey_day + PM_END:
                break
            
        if call_time <= survey_day + PM_END:  
            # start assigning EITHER calls from where we left off above
            pending_EITHER_p1s = [num for num in EITHER if num not in completed]
            i = 0
            while i < len(pending_EITHER_p1s):
                # get a block of numbers to call
                num_block = pending_EITHER_p1s[i:i+CALL_BLOCK_SIZE]
                for num in num_block:
                    subject = Subject.objects.get(number=str(num))
                    messenger_label = GROUPS[subject.group][SURVEYS.index(survey_label)]
                    survey = Survey.objects.get(name__contains=messenger_label+'_'+survey_label)
                    call = Call.objects.filter(survey=survey, subject=subject, date__gte=survey_day, priority=1)
                    if not bool(call):
                        call = Call(survey=survey, subject=subject, date=call_time, priority=1)
                        print ("adding call " + str(call))
                        call.save()
                        count += 1
                        completed.append(num)
                    
                i += CALL_BLOCK_SIZE
                call_time += CALL_BLOCK_INTERVAL_MINUTES
                
                if call_time > survey_day + PM_END:
                    break
    # end P1 assignments
    # with any remaining time left, assign P2's
    backup_calls(survey_label, list(set(pending_p1s)-set(PM)), survey_day + AM_START, survey_day + AM_END)
    backup_calls(survey_label, list(set(pending_p1s)-set(AM)), survey_day + PM_START, survey_day + PM_END)
                    
    print(str(count) + " new calls added.")   
    
def reminder_calls(days_from_start):
    count = 0
    reminder_survey = Survey.objects.get(name=REMINDER_NAME)
    
    all_nums = AM + EITHER + PM
    
    survey_day = STUDY_START + timedelta(days=days_from_start)
    call_time = survey_day + REMINDER_START
    
    subjs_completed = Subject.objects.filter(call__survey=reminder_survey, call__date__lt=survey_day, call__complete=True)
    completed = [int(subj.number) for subj in subjs_completed]
        
    pending_p1s = [num for num in all_nums if num not in completed]
    if pending_p1s:
        i = 0
        while i < len(pending_p1s):
            num_block = pending_p1s[i:i+CALL_BLOCK_SIZE]
            for num in num_block:
                subject = Subject.objects.get(number=str(num))
                call = Call.objects.filter(survey=reminder_survey, subject=subject, date__gte=survey_day, priority=1)
                if not bool(call):
                    call = Call(survey=reminder_survey, subject=subject, date=call_time, priority=1)
                    print ("adding reminder call " + str(call))
                    call.save()
                    count += 1
                    completed.append(num)
                
            i += CALL_BLOCK_SIZE
            call_time += CALL_BLOCK_INTERVAL_MINUTES
            
            if call_time > survey_day + REMINDER_END:
                break
    
    # end P1 assignments
    # with any remaining time left, assign P2's
    backup_calls(REMINDER_NAME, pending_p1s, survey_day + REMINDER_START, survey_day + REMINDER_END, survey=reminder_survey)
    
    print(str(count) + " new reminder calls added.")
       
# keep adding, as many times as possible,
# backup phone calls in the given range
def backup_calls(survey_label, nums, start_time, end_time, survey=False):
    scheduled_calls = []
    count = 0
    call_time = start_time
    i = 0
    while i < len(nums):
        scheduled_cnt = Call.objects.filter(survey__name__contains=survey_label, date=call_time).count()
        # NOTE: If this script is run more than once a day,
        # then this calculation will get screwed up
        if scheduled_cnt == 0:
            # get a block of numbers to call
            num_block = nums[i:i+CALL_BLOCK_SIZE]
            for num in num_block:
                subject = Subject.objects.get(number=str(num))
                if not survey:
                    messenger_label = GROUPS[subject.group][SURVEYS.index(survey_label)]
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

def main():
    if len(sys.argv) > 1:
        days_from_start = int(sys.argv[1])
    else:
        now = datetime.now()
        days_from_start = (now-STUDY_START).days

    calls(days_from_start)

main()

