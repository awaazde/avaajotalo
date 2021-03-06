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
from celery import group
from otalo.ao.models import Forum, Line, Message_forum, Message, User, Tag, Dialer
from otalo.surveys.models import Survey, Subject, Call, Prompt, Option, Param
import otalo_utils, stats_by_phone_num
from otalo.surveys import tasks as surveytasks

SOUND_EXT = ".wav"
OUTBOUND_SOUNDS_SUBDIR = 'forum/outbound/'
# Minimum number of times a caller
# must have called in to count in outbound broadcast
# (if getting subjects by log)
DEFAULT_CALL_THRESHOLD = 2

# Wait at least this many
# mins before sending a backup call
BACKUP_THRESH_MINS = 30

def subjects_by_numbers(numbers):
    # clean up the numbers, but don't limit to 10-digit (to alllow int'l bcasts)
    '''
    # This is just the work around for circular referece in ao.views, the ideal solution is to move get_phone_number method from views to some utils file.
    '''
    from otalo.ao.views import get_phone_number
    numbers = [get_phone_number(number, False) for number in numbers]
    numbers = filter(lambda n: n != None, numbers)
    
    # filter out black-listed numbers
    disallowed = User.objects.filter(number__in=numbers, allowed='n').values_list('number',flat=True)
    numbers = list(set(numbers) - set(list(disallowed)))
        
    return numbers_to_subjects(numbers)

'''
'    Given a list of numbers, return a list of subjects
'''
def numbers_to_subjects(numbers):
    subjects = []
    existing = Subject.objects.filter(number__in=numbers)
    existing_dict = {}
    new_subjects = []
    for s in existing:
        existing_dict[s.number] = s
    for n in numbers:
        if n in existing_dict:
            subjects.append(existing_dict[n])
        else:
            new_subjects.append(Subject(number=n))
    if new_subjects:
        Subject.objects.bulk_create(new_subjects)
        # get objects with their primary keys
        new_nums = [s.number for s in new_subjects]
        new_subjects = Subject.objects.filter(number__in=new_nums)
        new_subjects = [s for s in new_subjects]
        subjects += new_subjects
    return subjects

def subjects_by_tags(tags, line):
    tag_ids = [t.id for t in tags]
    numbers = User.objects.filter(Q(message__message_forum__tags__pk__in=tag_ids, message__message_forum__forum__line=line) | Q(tags__pk__in=tag_ids)).exclude(allowed='n').exclude(indirect_bcasts_allowed=False).distinct().values_list('number', flat=True)
    # execute the query to avoid complex joins in the next step
    numbers = list(numbers)
    return numbers_to_subjects(numbers)

# Assumes the messageforum is a top-level message
# and you want to bcast the whole thread (flattened)
def thread(messageforum, template, subjects, responseprompt, num_backups, start_date, bcastname=None):
    line = messageforum.forum.line_set.all()[0]
    language = OUTBOUND_SOUNDS_SUBDIR + line.language
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
    for su in subjects:
        bcast.subjects.add(su)
    for d in line.dialers.all():
        bcast.dialers.add(d)
    
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
    origpost = Prompt(file=messageforum.message.file.name, order=order, bargein=True, survey=bcast)
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
        
        responsecontent = Prompt(file=response.message.file.name, order=order, bargein=True, survey=bcast)
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

def regular_bcast(line, template, subjects, num_backups, start_date, bcastname=None):
    # create a clone from the template
    now = datetime.now()
    newname = bcastname
    if not newname or newname=='':
        newname = template.name.replace(Survey.TEMPLATE_DESIGNATOR, '') + '_' + datetime.strftime(now, '%b-%d-%Y')
    newname = newname[:128]
    bcast = clone_template(template, newname, num_backups, start_date)
    for su in subjects:
        bcast.subjects.add(su)
    for d in line.dialers.all():
        bcast.dialers.add(d)
    
    print("Created regular bcast "+ str(bcast) + " time " + str(bcast.created_on))
    return bcast

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

def schedule_bcasts(time=None, dialers=None):
    # gather all bcasts pending as of bcasttime
    # This is a comparison between group recipients and calls scheduled
    if not dialers:
        dialers = Dialer.objects.all()
    
    scheduled = []
    for dialer in dialers:
        bcasttime = time
        if bcasttime is None:
            bcasttime = datetime.now()
            
        print("Scheduling bcasts for dialer " + str(dialer) + "-" + date_str(bcasttime))
        '''
        '    Gather all bcasts in the last 12 hours (rolling)
        '    Limit the search since we can assume
        '    our scheduler is good enough (and we have enough
        '    capacity) to schedule a bcast within that time
        '''
        new_bcasts = {}
        backups = {}
        
        '''
        '    Get all possible numbers rather than relying on
        '    connected lines. This is in case there are surveys connected
        '    to numbers that aren't inbound lines (forum apps), like Xact numbers
        '
        '    Filter surveys for those that are connected to this dialer as an additional
        '    check. This is for the case where there are multiple dialers covering the same
        '    range of numbers, but with different prefixes. This happens with international
        '    dialing, where one PRI resources is used to dial multiple country codes. In that
        '    case different dialers with diff country codes are defined over the same number range.
        '    For that case you have to associate the broadcast to a specific dialer to specify
        '    which country code you want to dial with.
        '
        '''
        nums = dialer.get_dialer_numbers()
        bcasts = Survey.objects.filter(broadcast=True, created_on__gt=bcasttime-timedelta(hours=12), created_on__lte=bcasttime, number__in=nums, dialers=dialer).exclude(status=Survey.STATUS_CANCELLED)   
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
        
        num_scheduled = 0
        for survey, subject in flat:
            calls = []
            # don't schedule a subject multiple times across
            # dialers. Can happen if the subject's survey
            # is attached to multiple dialers
            if subject in scheduled:
                continue
            # assign calls up to maximum allowable in one burst
            if num_scheduled >= dialer.max_parallel_out:
                break
            latest_call = Call.objects.filter(survey=survey, subject=subject).order_by('-priority')
            priority = 1
            if bool(latest_call):
                latest_call = latest_call[0]
                # don't make this call if last call was made
                # less than BACKUP_THRESH_MINS ago
                if latest_call.date > bcasttime - timedelta(minutes=BACKUP_THRESH_MINS):
                    continue
                priority = latest_call.priority + 1
            
            calls.append(surveytasks.schedule_call.s(survey, dialer, subject, priority))
            #calls.append(surveytasks.test_task.s(survey, dialer, subject, priority, bcasttime))
            
            scheduled.append(subject)
            num_scheduled += 1
            
            g = group([t for t in calls])
            g.delay()
            

'''
****************************************************************************
************************** ANSWER_CALL RELATED *****************************
****************************************************************************
'''
def check_unsent_responses(interval_mins):
    interval = timedelta(minutes=interval_mins)
    now = datetime.now()
    # Get responses in the last INTERVAL_HOURS
    responses = Message_forum.objects.filter(message__lft__gt=1, message__date__gte=now-interval, status=Message_forum.STATUS_APPROVED)
    for response in responses:
        if not Prompt.objects.filter(file__contains=response.message.file.name) and response.forum.response_calls:
            answer_call(response.forum.line_set.all()[0], response)

def answer_call(line, answer):
    # get the immediate parent of this message
    fullthread = Message.objects.filter(Q(thread=answer.message.thread) | Q(pk=answer.message.thread.pk))
    ancestors = fullthread.filter(lft__lt=answer.message.lft, rgt__gt=answer.message.rgt).order_by('-lft')
    parent = ancestors[0]

    asker = Subject.objects.filter(number=parent.user.number)
    '''
    This function is called both explicitly from the view (UI) when a user uploads a response,
    as well as in a background cron-like task (celery) for cases where the response is recorded
    over IVR. Because of this, there are potential race conditions for a subject getting created
    and duplicate subjects were getting created.
    
    To fix, we've added a unique constraint on subject.number. So if we try to create here and there is
    a duplicate, we will get an integrity violation.
    
    Means we are working with a stale DB session here, let's just print the error and exit without doing
    anything further. 
    '''
    try:
        if not asker.exists():
            asker = Subject.objects.create(name=parent.user.name, number=parent.user.number)
        else:
            asker = asker[0]
    except IntegrityError as e:
        print(e)
        return
        
    now = datetime.now()
    num = line.outbound_number or line.number
    language = OUTBOUND_SOUNDS_SUBDIR + line.language
        
    s = Survey.objects.create(broadcast=True, name=Survey.ANSWER_CALL_DESIGNATOR +'_' + str(asker), complete_after=0, number=num, created_on=now, backup_calls=1)
    s.subjects.add(asker)
    for d in line.dialers.all():
        s.dialers.add(d)
    #print ("adding announcement survey " + str(s))
    order = 1
    
    # welcome
    welcome = Prompt.objects.create(file=language+"/welcome_responsecall.wav", order=order, bargein=True, survey=s)
    welcome_opt = Option.objects.create(number="", action=Option.NEXT, prompt=welcome)
    welcome_opt2 = Option.objects.create(number="1", action=Option.NEXT, prompt=welcome)
    order += 1
    
    original = Prompt.objects.create(file=parent.file.name, order=order, bargein=True, survey=s)
    original_opt = Option.objects.create(number="", action=Option.NEXT, prompt=original)
    original_opt2 = Option.objects.create(number="1", action=Option.NEXT, prompt=original)
    order += 1
    
    response = Prompt.objects.create(file=language+"/response_responsecall.wav", order=order, bargein=True, survey=s)
    response_opt = Option.objects.create(number="", action=Option.NEXT, prompt=response)
    response_opt2 = Option.objects.create(number="1", action=Option.NEXT, prompt=response)
    order += 1
        

    a = Prompt.objects.create(file=answer.message.file.name, order=order, bargein=True, survey=s)
    a_opt = Option.objects.create(number="", action=Option.NEXT, prompt=a)
    a_opt2 = Option.objects.create(number="1", action=Option.NEXT, prompt=a)
    order += 1
    
    if answer.forum.respondtoresponse_allowed:
        record = Prompt.objects.create(file=language+"/record_responsecall.wav", order=order, bargein=True, survey=s, delay=3000)
        record_opt = Option.objects.create(number="", action=Option.GOTO, prompt=record)
        param = Param.objects.create(option=record_opt, name=Param.IDX, value=order+2)
        record_opt2 = Option.objects.create(number="1", action=Option.RECORD, prompt=record)
        param2 = Param.objects.create(option=record_opt2, name=Param.MFID, value=answer.id)
        param3 = Param.objects.create(option=record_opt2, name=Param.ONCANCEL, value=order+2)
        order += 1
        
        recordthanks = Prompt.objects.create(file=language+"/thankyourecord_responsecall.wav", order=order, bargein=True, survey=s, delay=0)
        recordthanks_opt = Option.objects.create(number="", action=Option.NEXT, prompt=recordthanks)
        order += 1
    
    # thanks
    thanks = Prompt.objects.create(file=language+"/thankyou_responsecall.wav", order=order, bargein=True, survey=s)
    thanks_opt = Option.objects.create(number="", action=Option.NEXT, prompt=thanks)
    order += 1
            
'''
****************************************************************************
************************** UTILS *******************************************
****************************************************************************
'''
'''
'     Find out if there are any backup calls left to do
'     Exclude subjects with a complete call, or who have scheduled a call up to max number of backups
'     Do the exclude manually since Django doesn't correctly exclude on a relationship that was previously filtered on
'     e.g. Subject.objects.filter(call__survey=bcast).exclude(call__survey=bcast, call__complete=True) doesn't work!
'''
def get_pending_backup_calls(survey, max_backup_calls):     
    '''
    # Get subjects who are pending because of extra calls added based on hangup causes
    # don't use priority__lt because the query will pass as long as there exists any
    # call with a lesser priority. What we want to say is that a call does not exist
    # with the final priority
    '''
    hup_limit_queries = [Q(call__survey=survey, call__hangup_cause=cause) & ~Q(call__priority=Call.HUP_CAUSES_WITH_LIMIT[cause]+1) & ~Q(call__complete=True) for cause in Call.HUP_CAUSES_WITH_LIMIT.keys()]
    '''
    # The above subjects are pending, so exclude them from the exclude list generated below.
    # Do it as a separate exclude rather than in the filter because the filter includes
    # The Q statement with backup calls, which would have to say "AND doesn't have any
    # HUP Causes with limits", which does not seem possible to express through the ORM.
    # Otherwise a subject that needs extra calls because of HUP cause would be included
    # in the exclude list when backup calls have been exhausted 
    # (i.e. Q(call__priority=max_backup_calls+1) would be true)
    '''
    extra_calls_for_hup_cause = Subject.objects.filter(reduce(operator.or_, hup_limit_queries)).values_list('id',flat=True)
    #print('hup subjs '+str(hups))
    to_exclude = Subject.objects.filter(Q(call__complete=True) | Q(call__priority=max_backup_calls+1), call__survey=survey).exclude(pk__in=extra_calls_for_hup_cause).values_list('id', flat=True)
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
    
def date_str(date):
    #return date.strftime('%Y-%m-%d')
    return date.strftime('%m-%d-%y %H:%M')
    
'''
****************************************************************************
*************************** MAIN *******************************************
****************************************************************************
'''
if __name__=="__main__":
    if "--main" in sys.argv:        
        print("NONE")
    else:
        print("Command not found.")