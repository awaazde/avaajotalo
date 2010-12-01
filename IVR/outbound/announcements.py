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
from otalo.AO.models import Forum, Line, Message_forum, User
from otalo.AO.views import MESSAGE_STATUS_APPROVED
from otalo.surveys.models import Survey, Subject, Call, Prompt, Option
import otalo_utils, stats_by_phone_num

MEDIA_PATH = "/home/dsc/media/";

# These should be consistent with the constants
# in survey.lua
OPTION_NEXT = 1
OPTION_PREV = 2
OPTION_REPLAY = 3
OPTION_GOTO = 4

ANNOUNCEMENT_START_DATE = None
ANNOUNCEMENT_DURATION_DAYS = 2
ANNOUNCEMENT_START = timedelta(hours=7)
ANNOUNCEMENT_END = timedelta(hours=19)

# get callers to the line
# over the past X time
SUBJECT_PERIOD = timedelta(days=90)
MAX_N_NUMS = 300

CALL_BLOCK_SIZE = 10
# should match INTERVAL_MINS in survey.py and the frequency of the cron
CALL_BLOCK_INTERVAL_MINUTES = timedelta(minutes=10)
    
def subjects(f, line):
    calls = stats_by_phone_num.get_calls_by_number(filename=f, destnum=str(line.number), date_start=datetime.now()-SUBJECT_PERIOD, quiet=True)
    numbers = calls.keys()
    subjects = []
    
    for number in numbers[:MAX_N_NUMS]:
        u = User.objects.filter(number=number)
        if bool(u) and u[0].allowed == 'n':
            continue
        
        s = Subject.objects.filter(number = number)
        if not bool(s):
            s = Subject(number=str(number))
            print ("adding subject " + str(s))
            s.save()
            subjects.append(s)
        else:
            subjects.append(s[0])
    
    return subjects

def announce(announcements, name, line):
    prefix = line.dialstring_prefix
    suffix = line.dialstring_suffix
    language = line.language
    
    s = Survey.objects.filter(name=name)
    if not bool(s):
        s = Survey(name=name, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=2)
        print ("adding announcement survey " + str(s))
        s.save()
    
        # welcome
        welcome = Prompt(file=language+"/welcome_announce.mp3", order=1, bargein=False, survey=s)
        welcome.save()
        welcome_opt = Option(number="", action=OPTION_NEXT, prompt=welcome)
        welcome_opt.save()
        
        order=2
        for announcement in announcements:
            a = Prompt(file=announcement.message.content_file, order=order, bargein=False, survey=s)
            a.save()
            a_opt = Option(number="", action=OPTION_NEXT, prompt=a)
            a_opt.save()
            order += 1
        
        # thanks
        thanks = Prompt(file=language+"/thankyou_announce.mp3", order=order, bargein=False, survey=s)
        thanks.save()
        thanks_opt = Option(number="", action=OPTION_NEXT, prompt=thanks)
        thanks_opt.save()
        
        return s
    else:
        return s[0]
    
def announce_calls(announcement, subjects, announcement_start_date):
    count = 0
    # This is the only survey to send, so the
    # block is the entire duration period
    survey_block_days = ANNOUNCEMENT_DURATION_DAYS
    
    survey_start_day = announcement_start_date
    assigned_p1s = []
    for survey_block_day in range(survey_block_days):
        survey_day = survey_start_day + timedelta(days=survey_block_day)
        call_time = survey_day + ANNOUNCEMENT_START
        
        if len(assigned_p1s) < len(subjects):
            pending_p1s = [subj for subj in subjects if subj not in assigned_p1s]
            i = 0
            while i < len(pending_p1s):
                subj_block = pending_p1s[i:i+CALL_BLOCK_SIZE]
                for subject in subj_block:
                    call = Call.objects.filter(survey=announcement, subject=subject, priority=1)
                    if not bool(call):
                        call = Call(survey=announcement, subject=subject, date=call_time, priority=1)
                        print ("adding call " + str(call))
                        call.save()
                        count += 1
                        assigned_p1s.append(subject)
                    
                i += CALL_BLOCK_SIZE
                call_time += CALL_BLOCK_INTERVAL_MINUTES
                
                if call_time > survey_day + ANNOUNCEMENT_END:
                    break
        
        # end P1 assignments
        # with any remaining time left, assign P2's
        backup_calls(announcement, subjects, survey_day + ANNOUNCEMENT_START, survey_day + ANNOUNCEMENT_END)   

# keep adding, as many times as possible,
# backup phone calls in the given range
def backup_calls(survey, subjects, start_time, end_time):
    scheduled_calls = []
    count = 0
    call_time = start_time
    i = 0
    while i < len(subjects):
        scheduled_cnt = Call.objects.filter(date=call_time).count()
        if scheduled_cnt < 20:
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

def main():
    # get the forum
    if len(sys.argv) < 3:
        print("Wrong")
    else:
        f = sys.argv[1]
        forumid = sys.argv[2]
        
    if len(sys.argv) > 3:
        today = datetime.strptime(sys.argv[3], "%m-%d-%Y")
    else:
        now = datetime.now()
        today = datetime(year=now.year, month=now.month, day=now.day)
        
    forum = Forum.objects.get(pk=forumid)

    # check if there were new announcements within the past day
    announcements = Message_forum.objects.filter(forum=forum, message__date__gte=today, status=MESSAGE_STATUS_APPROVED).order_by('-message__date')
    if bool(announcements):
        line = forum.line_set.all()[0]
        oneday = timedelta(days=1)
        announcement_name = 'Announcement_' + forum.name + '_' + str(today)
        # start tomorrow
        announcement_start_date = today + oneday
        
        subjs = subjects(f, line)
        # create the announcement
        announcement = announce(announcements, announcement_name, line)
        # schedule the calls
        announce_calls(announcement, subjs, announcement_start_date)

main()

