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
import sys, os, operator
from operator import itemgetter
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Q, Max, Min
from otalo.ao.models import Forum, Line, Message_forum, Message, User, Tag, Dialer
from otalo.surveys.models import Survey, Subject, Call, Prompt, Option, Param
import otalo_utils, stats_by_phone_num

SOUND_EXT = ".wav"
# Minimum number of times a caller
# must have called in to count in outbound broadcast
# (if getting subjects by log)
DEFAULT_CALL_THRESHOLD = 2

DEF_INTERVAL_MINS = 5

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
        if user.allowed == 'n' or not user.indirect_bcasts_allowed:
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

def subjects_by_log(line, since, lastn=0, callthresh=DEFAULT_CALL_THRESHOLD):
    filename = settings.INBOUND_LOG_ROOT+str(line.id)+'.log'
    calls = stats_by_phone_num.get_numbers_by_date(filename=filename, destnum=str(line.number), date_start=since, quiet=True)
    numbers = calls.keys()
    subjects = []
    
    if lastn:
        numbers = numbers[:lastn]
        
    for number in numbers:
        u = User.objects.filter(number=number)
        if bool(u) and (u[0].allowed == 'n' or not u[0].indirect_bcasts_allowed):
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
            
    messages = Message_forum.objects.filter(forum=forum, message__date__gte=since, status=Message_forum.STATUS_APPROVED).order_by('-message__date')
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
        welcome_opt = Option(number="", action=Option.NEXT, prompt=welcome)
        welcome_opt.save()
        
        order=2
        for fname in filenames:
            msg = Prompt(file=fname, order=order, bargein=False, survey=s)
            msg.save()
            msg_opt = Option(number="", action=Option.NEXT, prompt=msg)
            msg_opt.save()
            order += 1
        
        # thanks
        thanks = Prompt(file=language+"/thankyou"+SOUND_EXT, order=order, bargein=False, survey=s)
        thanks.save()
        thanks_opt = Option(number="", action=Option.NEXT, prompt=thanks)
        thanks_opt.save()
        
        return s
    else:
        return s[0]

# Assumes the messageforum is a top-level message
# and you want to bcast the whole thread (flattened)
def thread(messageforum, template, responseprompt, num_backups, start_date, bcastname=None):
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
    responses = Message_forum.objects.filter(status = Message_forum.STATUS_APPROVED, message__thread=messageforum.message, message__lft__gt=1).order_by('message__lft')
    
    # create a clone from the template
    newname = bcastname
    if not newname or newname == '':
        newname = template.name.replace(Survey.TEMPLATE_DESIGNATOR, '') + '_' + str(messageforum)
    newname = newname[:128]
    bcast = clone_template(template, newname, num_backups, start_date)
    
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
            if option.action == Option.RECORD:
                oncancel = Param.objects.filter(option=option, name=Param.ONCANCEL)
                if bool(oncancel):
                    for p in oncancel:
                        p.value = int(p.value) + ntoshift
                        p.save()
            if option.action == Option.GOTO:
                goto = Param.objects.get(option=option, name=Param.IDX)
                goto.value = int(goto.value) + ntoshift
                goto.save()
        prompt.save()
    
    #fill in the missing prompt with the given thread
    order = thread_start
    origpost = Prompt(file=settings.MEDIA_ROOT + '/' + messageforum.message.content_file, order=order, bargein=True, survey=bcast)
    origpost.save()
    origpost_opt = Option(number="1", action=Option.NEXT, prompt=origpost)
    origpost_opt.save()
    origpost_opt2 = Option(number="", action=Option.NEXT, prompt=origpost)
    origpost_opt2.save()
    order += 1
    
    for i in range(responses.count()):
        response = responses[i]
        if i == 0:
            responseintro = Prompt(file=language+'/firstresponse'+SOUND_EXT, order=order, bargein=True, survey=bcast)
        else:
            responseintro = Prompt(file=language+'/nextresponse'+SOUND_EXT, order=order, bargein=True, survey=bcast)
        responseintro.save()
        responseintro_opt = Option(number="1", action=Option.NEXT, prompt=responseintro)
        responseintro_opt.save()
        responseintro_opt2 = Option(number="", action=Option.NEXT, prompt=responseintro)
        responseintro_opt2.save()
        order += 1
        
        responsecontent = Prompt(file=settings.MEDIA_ROOT + '/' + response.message.content_file, order=order, bargein=True, survey=bcast)
        responsecontent.save()
        responsecontent_opt = Option(number="1", action=Option.NEXT, prompt=responsecontent)
        responsecontent_opt.save()
        responsecontent_opt2 = Option(number="", action=Option.NEXT, prompt=responsecontent)
        responsecontent_opt2.save()
        order += 1
    
    if responseprompt:
         # record
        record = Prompt(file=language+"/recordmessage"+SOUND_EXT, order=order, bargein=True, survey=bcast, name='Response' )
        record.save()
        record_opt = Option(number="", action=Option.RECORD, prompt=record)
        record_opt.save()
        param = Param(option=record_opt, name=Param.MFID, value=messageforum.id)
        param.save()
        maxlen = messageforum.forum.max_user_resp_len or Forum.MAX_USER_RESP_LEN_DEF
        param2 = Param(option=record_opt, name=Param.MAXLENGTH, value=str(maxlen))
        param2.save()
        if not messageforum.forum.confirm_recordings:
            param3 = Param(option=record_opt, name=Param.CONFIRM_REC, value="0")
            param3.save()
        record_opt2 = Option(number="1", action=Option.RECORD, prompt=record)
        record_opt2.save()
        param4 = Param(option=record_opt2, name=Param.MFID, value=messageforum.id)
        param4.save()
        param5 = Param(option=record_opt2, name=Param.MAXLENGTH, value=str(messageforum.forum.maxlength))
        param5.save()
        if not messageforum.forum.confirm_recordings:
            param6 = Param(option=record_opt2, name=Param.CONFIRM_REC, value="0")
            param6.save()
    
    return bcast

def regular_bcast(template, num_backups, start_date, bcastname=None):
    # create a clone from the template
    now = datetime.now()
    newname = bcastname
    if not newname or newname=='':
        newname = template.name.replace(Survey.TEMPLATE_DESIGNATOR, '') + '_' + datetime.strftime(now, '%b-%d-%Y')
    newname = newname[:128]
    return clone_template(template, newname, num_backups, start_date)

def clone_template(template, newname, num_backups, start_date):
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
    bcast.backup_calls = num_backups
    bcast.created_on = start_date
    bcast.save()
    
    return bcast

'''
'    This function is meant to wake up every
'    INTERVAL_MINS and run scheduling
'    algorithm on all pending bcasts
'''

def  schedule_bcasts(time=None, dialers=None):
    # gather all bcasts pending as of bcasttime
    # This is a comparison between group recipients and calls scheduled
    if not dialers:
        dialers = Dialer.objects.all()
    
    for dialer in dialers:
        bcasttime = time
        if bcasttime is None:
            bcasttime = get_most_recent_interval(dialer)
            
        print("Scheduling bcasts for time: "+ date_str(bcasttime))
        '''
        '    Gather all bcasts in the last 12 hours (rolling)
        '    Limit the search since we can assume
        '    our scheduler is good enough (and we have enough
        '    capacity) to schedule a bcast within that time
        '''
        new_bcasts = {}
        backups = {}
        
        lines = Line.objects.filter(dialers=dialer)
        nums = [line.outbound_number or line.number for line in lines]
        bcasts = Survey.objects.filter(broadcast=True, created_on__gt=bcasttime-timedelta(hours=12), created_on__lte=bcasttime, number__in=nums)   
        for bcast in bcasts:
            #print("pending bcast: "+ str(bcast))
            scheduled_subjs = Call.objects.filter(survey=bcast).values('subject__number').distinct()
            # next line purely for query optimization purposes
            scheduled_subjs = [subj.values()[0] for subj in scheduled_subjs]
            recipients = bcast.subjects.all()
            to_sched = recipients.exclude(number__in=scheduled_subjs)
            num_backup_calls = bcast.backup_calls or 0
            #print("to schedule: "+ str(to_sched))
            if to_sched:
                new_bcasts[bcast] = to_sched
            elif num_backup_calls > 0:
                #print("checking backup calls for " + str(group))
                '''
                '     Find out if there are any backup calls left to do
                '     Exclude subjects with a complete call, or who have scheduled a call up to max number of backups
                '     Do the exclude manually since Django doesn't correctly exclude on a relationship that was previously filtered on
                '     e.g. Subject.objects.filter(call__survey=bcast).exclude(call__survey=bcast, call__complete=True) doesn't work!
                '''
                to_sched = get_pending_backup_calls(bcast, num_backup_calls)
                
                if to_sched:
                    backups[bcast] = to_sched
                    
        '''            
        ' Implementing Shortest Remaining Finish Time discipline (non-preemptive)
        ' Sort the lists in ascending order
        ' Sort by priority first, so P1 bcasts always happen first
        ' NOTE that this SRFT will respect finish time above backup call priority.
        ' So a task with 5 P3 calls will get scheduled ahead of a task with 10 P2s
        '''
        sorted_newbcasts = sorted(new_bcasts.iteritems(), key=lambda (k,v): v.count())
        sorted_backups = sorted(backups.iteritems(), key=lambda (k,v): len(v))
        sorted_bcasts = sorted_newbcasts + sorted_backups
        
        # sorted_bcasts is a list of tuples: [(s1, [u1,u2]), (s2, [u3,u4,u5,u6,u7]), ...]
        # now flatten it out to just get bcast-user pairs
        flat = []
        for s,subjects in sorted_bcasts:
            for sub in subjects:            
                flat.append([s,sub])

        #print("sorted list: "+str(flat))       
        
        # assign calls as they are
        # found to be available
        scheduled = {}
        num_available = dialer.max_parallel - Call.objects.filter(dialstring_prefix=dialer.dialstring_prefix, date=bcasttime).count()
        #print("prefix "+prefix+" maxpara="+str(PROFILES[prefix]['maxparallel'])+" existing call count="+str(Call.objects.filter(dialstring_prefix=prefix, date=bcasttime).count()))
        to_sched = flat[:num_available]
        for survey, subject in to_sched:            
            priority = Call.objects.filter(survey=survey, subject=subject).aggregate(Max('priority'))
            priority = priority.values()[0]
            if priority:
                priority += 1
            else:
                priority = 1
            call = Call.objects.create(survey=survey, dialstring_prefix=dialer.dialstring_prefix, subject=subject, date=bcasttime, priority=priority)
            print('Scheduled call '+ str(call))
            
'''
****************************************************************************
************************** UTILS *******************************************
****************************************************************************
'''
        
def get_most_recent_interval(dialer):
    interval = datetime.now()
    # round up to nearest minute
    if interval.second != 0 or interval.microsecond != 0:
        interval = datetime(year=interval.year, month=interval.month, day=interval.day, hour=interval.hour, minute=interval.minute)
        # go into the future in order to avoid
        # race conditions with survey.py
        interval += timedelta(minutes=2)
        
    # Locate most recent stack of
    # scheduled messages
    for i in range(dialer.interval_mins or DEF_INTERVAL_MINS,-1,-1,-1):
        nums = get_dialer_numbers(dialer)
        if bool(Call.objects.filter(survey__number__in=nums, survey__broadcast=True, date=interval-timedelta(minutes=i))):
            interval -= timedelta(minutes=i)
            break
    print("Found most recent interval: "+date_str(interval)) 
    return interval

'''
' Utility function to check which members need backup calls scheduled
'''
def get_pending_backup_calls(survey, max_backup_calls):        
    to_exclude = Subject.objects.filter(Q(call__complete=True) | Q(call__priority=max_backup_calls+1), call__survey=survey).values('id')
    to_exclude = [s.values()[0] for s in to_exclude]
    to_sched = Subject.objects.filter(call__survey=survey).exclude(pk__in=to_exclude).annotate(max_pri=Max('call__priority')).values('number','max_pri')
    #print('to_sched: ' + str(to_sched))
    to_sched = [tuple(s.values()) for s in to_sched]
    #print('to_sched tuples: ' + str(to_sched))
    # add to schedule queue ordered by priority so that all nth backups go out before n+1
    to_sched = sorted(to_sched, key=itemgetter(1))
    #print('to_sched sorted: ' + str(to_sched))
    to_sched = [Subject.objects.filter(number=s[0])[0] for s in to_sched]
    #print('backups to sched: '+str(to_sched))
    
    return to_sched


'''
'    Get all possible numbers associated with this dialer
'''
def get_dialer_numbers(dialer):
    nums = []
    for i in range(dialer.max_nums):
        nums.append(str(int(dialer.base_number)+1))
    return nums
    
def date_str(date):
    #return date.strftime('%Y-%m-%d')
    return date.strftime('%m-%d-%y %H:%M')
    
'''
****************************************************************************
*************************** MAIN *******************************************
****************************************************************************
'''
if __name__=="__main__":
    if "--schedule_bcasts_by_dialers" in sys.argv:
        dialers = Dialers.objects.all()
        if len(sys.argv) > 2:
            dialerids = sys.argv[2].split(',')
            dialerids = [int(id.strip()) for id in dialerids]
            dialers = dialers.filter(pk__in=dialerids)
        
        schedule_bcasts(dialers=dialers)
    if "--schedule_bcasts_by_base_numbers" in sys.argv:
        numbers = sys.argv[2].split(',')
        numbers = [num.strip() for num in numbers]
        dialers = Dialer.objects.filter(base_number__in=numbers)
        schedule_bcasts(dialers=dialers)
    elif "--gws_dialers" in sys.argv:
        authid = sys.argv[2]
        pri_dialer = Dialer.objects.get(pk=int(sys.argv[3]))
        print("PRI Dialer: " + str(pri_dialer))
        lines = Line.objects.filter(forums__admin__auth_user__pk=int(authid))
        
        for l in lines:
            #print('line '+str(l))
            if 'freetdm' in l.dialstring_prefix:
                l.dialers.add(pri_dialer)
                print("Adding PRI dialer to line "+ str(l))
            else:
                d = Dialer.objects.filter(dialstring_prefix=l.dialstring_prefix)
                if bool(d):
                    d = d[0]
                    print("Found VoIP dialer "+str(d)+" for line "+str(l))
                else:
                    d = Dialer.objects.create(base_number=pri_dialer.base_number, type=Dialer.DIALER_TYPE_VOIP, max_nums=pri_dialer.max_nums, max_parallel=9999, interval_mins=Dialer.MIN_INTERVAL_MINS, dialstring_prefix=l.dialstring_prefix)                
                    print("Created VoIP dialer "+str(d)+" for line "+str(l))
                    
                l.dialers.add(d)     
        
    elif "--main" in sys.argv:
        bases = {1:'7961907700', 2:'7967776000', 3:'7967775500', 5:'7961555000', 6:'7967776100', 7:'7967776200', 8:'7930118999'}
        #bases = {2:'7930142000'}
        dialers=[]
        
        for slot,base in bases.iteritems():
            d = Dialer.objects.create(base_number=base, type=Dialer.DIALER_TYPE_PRI, max_parallel=25, max_nums=100, interval_mins=Dialer.MIN_INTERVAL_MINS, dialstring_prefix='freetdm/grp'+str(slot)+'/a/0')
            print("Created dialer "+ str(d))
            dialers.append(d)
        
        lines = {1:['61907700', '61907707', '61907711', '61907788', '61907754', '61907755', '61907744'], 2:['67776000', '67776066'], 6:['67776177'], 7:['67776222']}
        #lines = {2: ['30142000', '30142011']}
        for slot,nums in lines.iteritems():
            d = Dialer.objects.filter(dialstring_prefix__contains='grp'+str(slot))[0]
            for num in nums:
                lines = Line.objects.filter(number__contains=num)
                if bool(lines):
                    for l in lines: 
                        l.dialers.add(d)
                        print ("added dialer "+str(d) + " to line " + str(l))
                else:
                    print("line not found: "+str(num))
    else:
        print("Command not found.")