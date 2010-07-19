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
from otalo.surveys.models import Survey, Subject, Call
from random import shuffle

# This should match with how often the cron runs
EITHER = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22]
AM = [30,31,32,33]
PM = [34,35,36,37]

AM_START = timedelta(hours=6)
AM_END = timedelta(hours=9)
PM_START = timedelta(hours=18)
PM_END = timedelta(hours=21)

# NOTE: surveys will be scheduled in order of their survey_id
#        if there are gaps in the ids, there will be a gap in the
#        time period between surveys
SURVEYS = [1,2,3,4]

STUDY_START = datetime(year=2010, month=8, day=1)
STUDY_DURATION_DAYS = 8

CALL_BLOCK_SIZE = 10
# should match INTERVAL_MINS in survey.py and the frequency of the cron
CALL_BLOCK_INTERVAL_MINUTES = timedelta(minutes=10)

def add_surveys():
    count = 0
    for survey_id in SURVEYS:
        s = Survey.objects.filter(id=survey_id)
        if not bool(s):
            s = Survey(id=survey_id)
            print ("adding " + str(s))
            s.save()
            count += 1
    print(str(count) + " new surveys added.")
            
def add_subjects():
    count = 0
    
    all = EITHER + AM + PM
    for number in all:
        s = Subject.objects.filter(number = number)
        if not bool(s):
            s = Subject(number=str(number))
            print ("adding " + str(s))
            s.save()
            count += 1
    
    print(str(count) + " new subjects added.")

def schedule_calls():
    count = 0
    survey_block_days = STUDY_DURATION_DAYS / len(SURVEYS)
    
    all_nums = AM + EITHER + PM

    for survey_id in SURVEYS:
        survey = Survey.objects.get(pk=survey_id)
        assigned_p1s = []
        
        # surveys are spread out evenly over the study period.
        # IMPORTANT ASSUMPTIONS: 
        #    1. There is at least one day for each survey
        #    2. Within each survey period there is enough time to schedule P1s for
        #       every number given the CALL_BLOCK_SIZE and the CALL_BLOCK_INTERVAL
        survey_start_day = STUDY_START + timedelta(days=survey_block_days) * (survey_id-1)
        
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
                        call = Call.objects.filter(survey=survey, subject=subject, priority=1)
                        if not bool(call):
                            call = Call(survey=survey, subject=subject, date=call_time, priority=1)
                            print ("adding " + str(call))
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
                            call = Call.objects.filter(survey=survey, subject=subject, priority=1)
                            if not bool(call):
                                call = Call(survey=survey, subject=subject, date=call_time, priority=1)
                                print ("adding " + str(call))
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
                        call = Call.objects.filter(survey=survey, subject=subject, priority=1)
                        if not bool(call):
                            call = Call(survey=survey, subject=subject, date=call_time, priority=1)
                            print ("adding " + str(call))
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
                            call = Call.objects.filter(survey=survey, subject=subject, priority=1)
                            if not bool(call):
                                call = Call(survey=survey, subject=subject, date=call_time, priority=1)
                                print ("adding " + str(call))
                                call.save()
                                count += 1
                                assigned_p1s.append(num)
                            
                        i += CALL_BLOCK_SIZE
                        call_time += CALL_BLOCK_INTERVAL_MINUTES
                        
                        if call_time > survey_day + PM_END:
                            break
            # end P1 assignments
            # with any remaining time left, assign P2's
            add_backup_calls(survey, AM+EITHER, survey_day + AM_START, survey_day + AM_END)
            add_backup_calls(survey, PM+EITHER, survey_day + PM_START, survey_day + PM_END)
                    
    print(str(count) + " new calls added.")            

# keep adding, as many times as possible,
# backup phone calls in the given range
def add_backup_calls(survey, nums, start_time, end_time):
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
                call = Call.objects.filter(survey=survey, subject=subject, date=call_time, priority=2)
                if not bool(call):
                    call = Call(survey=survey, subject=subject, date=call_time, priority=2)
                    print ("adding " + str(call))
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
    
    print(str(count) + " new calls added.")   
    
    return scheduled_calls
    				
def main():
    add_surveys()
    add_subjects()
    schedule_calls()

main()
