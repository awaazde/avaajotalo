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
import sys, os
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Q
from otalo.AO.models import Forum, Line, Message_forum, Message, User, Tag
from otalo.AO.views import MESSAGE_STATUS_APPROVED
from otalo.surveys.models import Survey, Subject, Call, Prompt, Option
import otalo_utils, stats_by_phone_num

TEMPLATE_DESIGNATOR = 'TEMPLATE'
# These should be consistent with the constants
# in survey.lua
OPTION_NEXT = 1
OPTION_PREV = 2
OPTION_REPLAY = 3
OPTION_GOTO = 4
OPTION_RECORD = 5
OPTION_INPUT = 6
OPTION_TRANSFER = 7;

SOUND_EXT = ".wav"

DEFAULT_DURATION_DAYS = 2
DEFAULT_START_TIME = timedelta(hours=7)
DEFAULT_END_TIME = timedelta(hours=19)
# Minimum number of times a caller
# must have called in to count in outbound broadcast
# (if getting subjects by log)
DEFAULT_CALL_THRESHOLD = 2
# get callers to the line
# over the past X time
SUBJECT_PERIOD = timedelta(days=90)
MAX_N_NUMS = 300

CALL_BLOCK_SIZE = 10
# should match INTERVAL_MINS in survey.py and the frequency of the cron
CALL_BLOCK_INTERVAL_MINUTES = timedelta(minutes=10)

def subjects_by_numbers(numbers):
    subjects = []
    
    for number in numbers:
        number = number.strip()
        number = number[-10:]
        if number == '':
            continue
        u = User.objects.filter(number=number)
        if bool(u) and u[0].allowed == 'n':
            continue
        
        s = Subject.objects.filter(number = number)
        if not bool(s):
            s = Subject(number=str(number))
            #print ("adding subject " + str(s))
            s.save()
            subjects.append(s)
        else:
            subjects.append(s[0])

    return subjects

def subjects_by_tags(tags, line):
    subjects = []
    
    users = User.objects.filter(Q(message__message_forum__tags__in=tags, message__message_forum__forum__line=line) | Q(tags__in=tags)).distinct()
    for user in users:
        if user.allowed == 'n':
            continue
        s = Subject.objects.filter(number = user.number)
        if not bool(s):
            s = Subject(number=user.number)
            #print ("adding subject " + str(s))
            s.save()
            subjects.append(s)
        else:
            subjects.append(s[0])
    
    return subjects

def subjects_by_log(logfile, line, since, lastn=0, callthresh=DEFAULT_CALL_THRESHOLD):
    calls = stats_by_phone_num.get_calls_by_number(filename=logfile, destnum=str(line.number), date_start=since, quiet=True)
    numbers = calls.keys()
    subjects = []
    
    if lastn:
        numbers = numbers[:lastn]
        
    for number in numbers:
        u = User.objects.filter(number=number)
        if bool(u) and u[0].allowed == 'n':
            continue
        
        s = Subject.objects.filter(number = number)
        if not bool(s):
            s = Subject(number=str(number))
            #print ("adding subject " + str(s))
            s.save()
            subjects.append(s)
        else:
            subjects.append(s[0])
    
    return subjects

def single(file, line):
    # save the file
    now = datetime.now()
    extension = file.name[file.name.index('.'):]
    filename = now.strftime("%m-%d-%Y_%H%M%S") + extension
    filename_abs = settings.MEDIA_ROOT + '/' + filename
    destination = open(filename_abs, 'wb')
    #TODO: test to see that this overwrites an existing file with that name
    for file in file.chunks():
        destination.write(chunk)
    os.chmod(filename_abs, 0644)
    destination.close()
    name = 'Single_' + filename
    
    return create_bcast_survey(line, [filename_abs], name)

def forum(forum, line, since=None):
    now = datetime.now()
    today = datetime(year=now.year, month=now.month, day=now.day)
        
    if since:
        since = datetime.strptime(sys.argv[3], "%m-%d-%Y")
    else:
        since = today
            
    messages = Message_forum.objects.filter(forum=forum, message__date__gte=since, status=MESSAGE_STATUS_APPROVED).order_by('-message__date')
    if messages:
        filenames = []
        for msg in messages:
            filenames.append(settings.MEDIA_ROOT+ '/' + msg.message.content_file)
        
        name = 'Forum_' + forum.name + '_' + str(today)
        return create_bcast_survey(line, filenames, name)

def create_bcast_survey(line, filenames, surveyname):
    prefix = line.dialstring_prefix
    suffix = line.dialstring_suffix
    language = line.language
    if line.outbound_number:
        num = line.outbound_number
    else:
        num = line.number
        
    s = Survey.objects.filter(name=surveyname)
    if not bool(s):
        s = Survey(name=surveyname, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0, number=num, broadcast=True)
        #print ("adding announcement survey " + str(s))
        s.save()
    
        # welcome
        welcome = Prompt(file=language+"/welcome"+SOUND_EXT, order=1, bargein=False, survey=s)
        welcome.save()
        welcome_opt = Option(number="", action=OPTION_NEXT, prompt=welcome)
        welcome_opt.save()
        
        order=2
        for fname in filenames:
            msg = Prompt(file=fname, order=order, bargein=False, survey=s)
            msg.save()
            msg_opt = Option(number="", action=OPTION_NEXT, prompt=msg)
            msg_opt.save()
            order += 1
        
        # thanks
        thanks = Prompt(file=language+"/thankyou"+SOUND_EXT, order=order, bargein=False, survey=s)
        thanks.save()
        thanks_opt = Option(number="", action=OPTION_NEXT, prompt=thanks)
        thanks_opt.save()
        
        return s
    else:
        return s[0]

# Assumes the messageforum is a top-level message
# and you want to bcast the whole thread (flattened)
def thread(messageforum, template, responseprompt):
    line = messageforum.forum.line_set.all()[0]
    prefix = line.dialstring_prefix
    suffix = line.dialstring_suffix
    language = line.language
    if line.outbound_number:
        num = line.outbound_number
    else:
        num = line.number
    
    # find the hole in the survery_template
    # job interview questions come in handy after all
    prompts = Prompt.objects.filter(survey=template).order_by('order')
    summation = 0
    order_tot = 0
    for i in range(prompts.count()):
        order_tot += prompts[i].order
        summation += i+1
        
    thread_start = summation + i + 2 - order_tot
    if (thread_start == 0):
        thread_start = i+1
    responses = Message.objects.filter(thread=messageforum.message, lft__gt=1).order_by('lft')
    
    # create a clone from the template
    newname = template.name.replace(TEMPLATE_DESIGNATOR, '') + '_' + str(messageforum)
    newname = newname[:128]
    # avoid duplicating forums that point to the template
    forums = Forum.objects.filter(bcast_template=template)
    for forum in forums:
        forum.bcast_template = None
        forum.save()
    oldtemp = template
    bcast = template.deepcopy(newname=newname)
    for forum in forums:
        forum.bcast_template = oldtemp
        forum.save()
        
    bcast.template = False
    bcast.broadcast = True
    bcast.save()
    
    # shift the old prompts before we add new ones to override the order
    toshift = Prompt.objects.filter(survey=bcast, order__gt=thread_start)
    # the gap left already keeps one index open
    # so only need to make room for any responses
    ntoshift = 2 * responses.count()
    if responseprompt:
        # one more space for record message prompt
        ntoshift += 1
    for prompt in toshift:
        prompt.order += ntoshift
        for option in Option.objects.filter(prompt=prompt):
            if option.action == OPTION_RECORD and option.action_param2:
                option.action_param2 = int(option.action_param2) + ntoshift
                option.save()
        prompt.save()
    
    #fill in the missing prompt with the given thread
    order = thread_start
    origpost = Prompt(file=settings.MEDIA_ROOT + '/' + messageforum.message.content_file, order=order, bargein=True, survey=bcast)
    origpost.save()
    origpost_opt = Option(number="1", action=OPTION_NEXT, prompt=origpost)
    origpost_opt.save()
    origpost_opt2 = Option(number="", action=OPTION_NEXT, prompt=origpost)
    origpost_opt2.save()
    order += 1
    
    for response in responses:
        if response.lft == 2:
            responseintro = Prompt(file=language+'/firstresponse'+SOUND_EXT, order=order, bargein=True, survey=bcast)
        else:
            responseintro = Prompt(file=language+'/nextresponse'+SOUND_EXT, order=order, bargein=True, survey=bcast)
        responseintro.save()
        responseintro_opt = Option(number="1", action=OPTION_NEXT, prompt=responseintro)
        responseintro_opt.save()
        responseintro_opt2 = Option(number="", action=OPTION_NEXT, prompt=responseintro)
        responseintro_opt2.save()
        order += 1
        
        responsecontent = Prompt(file=settings.MEDIA_ROOT + '/' + response.content_file, order=order, bargein=True, survey=bcast)
        responsecontent.save()
        responsecontent_opt = Option(number="1", action=OPTION_NEXT, prompt=responsecontent)
        responsecontent_opt.save()
        responsecontent_opt2 = Option(number="", action=OPTION_NEXT, prompt=responsecontent)
        responsecontent_opt2.save()
        order += 1
    
    if responseprompt:
         # record
        record = Prompt(file=language+"/recordmessage"+SOUND_EXT, order=order, bargein=True, survey=bcast, name='Response' )
        record.save()
        record_opt = Option(number="", action=OPTION_RECORD, prompt=record, action_param3=messageforum.id)
        record_opt.save()
        record_opt2 = Option(number="1", action=OPTION_RECORD, prompt=record, action_param3=messageforum.id)
        record_opt2.save()
    
    return bcast

def broadcast_calls(survey, subjects, bcast_start_date, bcast_start_time=DEFAULT_START_TIME, bcast_end_time=DEFAULT_END_TIME, duration=DEFAULT_DURATION_DAYS, backups=False):
    count = 0
    # This is the only survey to send, so the
    # block is the entire duration period
    survey_block_days = duration
    
    survey_start_day = bcast_start_date
    assigned_p1s = []
    for survey_block_day in range(survey_block_days):
        survey_day = survey_start_day + timedelta(days=survey_block_day)
        call_time = survey_day + bcast_start_time
        
        if len(assigned_p1s) < len(subjects):
            pending_p1s = [subj for subj in subjects if subj not in assigned_p1s]
            i = 0
            while i < len(pending_p1s):
                subj_block = pending_p1s[i:i+CALL_BLOCK_SIZE]
                for subject in subj_block:
                    call = Call.objects.filter(survey=survey, subject=subject, priority=1)
                    if not bool(call):
                        call = Call(survey=survey, subject=subject, date=call_time, priority=1)
                        #print ("adding call " + str(call))
                        call.save()
                        count += 1
                        assigned_p1s.append(subject)
                    
                i += CALL_BLOCK_SIZE
                call_time += CALL_BLOCK_INTERVAL_MINUTES
                
                if call_time > survey_day + bcast_end_time:
                    break
        
        # end P1 assignments
        # with any remaining time left, assign P2's
        if backups:
            backup_calls(survey, subjects, survey_day + bcast_start_time, survey_day + bcast_end_time)   

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
                    #print ("adding call " + str(call))
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
    
    #print(str(count) + " new backup calls added.")   
    
    return scheduled_calls

def main():
    # get the forum
#    if len(sys.argv) < 2:
#        print("Wrong")
#    else:
#        f = sys.argv[1]
#    
#    #subjects_by_numbers(['333','444'])
#    ts = Tag.objects.filter(tag__in=['Banana'])
#    subjects_by_tags(ts)
#    
#    now = datetime.now()
#    threemosago = now - timedelta(days=90)
#    ln = Line.objects.get(pk=1)
#    s = subjects_by_log(f, ln, threemosago, lastn=300, callthresh=DEFAULT_CALL_THRESHOLD)
#    
#    content = open(f, 'r')
#    b = single(content, ln)
#    messages = Message_forum.objects.filter(pk__in=[1,2])
#    forum = Forum.objects.get(pk=2)
#    b2 = messages(messages, ln)
#    b3 = forum(forum, ln, since=None)
#    
#    now = datetime.now()
#    today = datetime(year=now.year, month=now.month, day=now.day)
    #broadcast_calls(b, s, today)
    mf = Message_forum.objects.get(pk=1844)
    temp = Survey.objects.get(pk=4)
    thread(mf, temp)

#main()
