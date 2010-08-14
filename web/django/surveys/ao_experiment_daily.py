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
EITHER = [2877222260,9723037029,9624820573,9726766913,2742295194,9327572297,9978063662,9925795859,9974572646,9913127379,9909484864,9909480769,9909397629,9904689792,9904075323,9898836049,9898533546,9879732707,9879350157,9825875631,9909189931,9726660105,9725729441,9714560511,9714327015,9714246198,9624086950,9574978416,9574416890,9574188431,9429352624,9227352190,9904622685,9824262550,9428671603,9723332236,9426373684,9428500591,9925525663,9426554773,9979711961,9979087320,9714001359,9427535277,9428984533,9726485205,9724632394,9978719704,9924284505,9725850145,8140252102,9979273464,9909621073,9879841603,9879069329,9825524687,9825279001,9726883910,9737369863,9737694692,9824784871,9879274611,9825951687,9723149575]
AM = [9925546520,7567331806,2737236315,9998952575,9974540063,9913921466,9925716672,9723800850,9726331577,9429251501,9228816198,9099514664,9904259110,9909840752,9428136567,9428063295,8000688598,9998088731,9925880755,9924584010,9913657611,9624372044,9909233817,9574013934,9327538732,9725331043,9979459741,9723181832,9974541880,9909893827,9712756833]
PM = [9726051598,9909839117,9428557642,9924500374,9825578331,9824171748,9724700753,9714934982,9925513984,9427379911,2697342397,9428126906,9016249969,9924341087,9909759893,9724884238,8140437612,2833295141,7567164618,9925364656,9913398273,9601567245,9586132465,9426320340,9998318554,9624045636,9978173169,9925660140,9825726214,9727696899,9726814182,9638346557,8980271921,9925583401,9712198296,9824367539,9724443284,9427249401,9016840997,8141847594,9913991823,9893966806,9979314531,9724581388,9624451766,9913332272,9427555857,9638660663,9924355148,9427564859,9974484853,9925145434,9924528796,9913422018,9912011936,9909492653,9909399897,9909070236,9904622512,9726592964,8140255231,2744253277,9726061931,9428987491,9428241676,9979625862,9879876394,9974961909,9974122869,9925310504,9824829592,9924885762,9924773951,9737232762,9725102377,9724774625,9714959731,9714736647,9714148023,9687433392,9624779381,9601145413,9586312853,9904001667,9537559883,9537293638,9429943304,9429609357,9429527617,9228064441,8140877835,9925684373,9687193246,9974669323,9714785932,9638844584,9998664234,9723887815,9427145486,9974641216,9978163140,9429269788,9276502212,9978564476,9879318158,9586058070,9925316417,9924834046,9427667496,9727281416,9974852923,9925618145,9427330743,9978305087,9978383329,9727128162,9904634418,9726356814,9429140966,9879337160,9428568904,9724537977,9638391892,9099193500,9726659436,9723658772,9429218227,9016638646,9925508550,9327477984,9913282079,9913213272,9909847737,9904925740,9904575420,9825378326,9726046695,9726186380,9726477492,9726489610,9726665628,9879879905,9727281261,9727608301,9727641947,9727642827,9727689590,9727696645,9737362944,9737389044,9737583425,9737871915,9824241614,9824928848,9824992905,9879632462,9879319268,9879188943,9879099378,9879044080,9879022533,9825336919,9824967764,9737622557,9737386565,9737125763,9727307784,9726668506,9726592014,9726492370,9726406074,9726384118,9726324249,9725061283,9725040752,9724522159,9723684923,9723011177,9638099359,9726074838,9727424483,9727722178]

GROUPS = [["REMINDER_DUMMY","E1","E2","P1","P2","E1","P1","E2","P2"], ["REMINDER_DUMMY","E2","E1","P2","P1","E2","P2","E1","P1"], ["REMINDER_DUMMY","P1","P2","E1","E2","P1","E1","P2","E2"], ["REMINDER_DUMMY","P2","P1","E2","E1","P2","E2","P1","E1"]]

AM_START = timedelta(hours=6)
AM_END = timedelta(hours=9)
PM_START = timedelta(hours=18)
PM_END = timedelta(hours=21)

# The actual surveys to run, in the order to run them in
SURVEYS = ["REMINDER", "T1_BCALL", "T2_BCALL", "T3_BCALL", "T4_BCALL", "T5_BCALL", "T6_BCALL", "T7_BCALL", "T8_BHOLD"]

STUDY_START = datetime(year=2010, month=8, day=14)
STUDY_DURATION_DAYS = 18

REMINDER_START = timedelta(hours=6)
REMINDER_END = timedelta(hours=21)

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

