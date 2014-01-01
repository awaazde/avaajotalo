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
from celery import shared_task
from otalo.surveys.models import *
from otalo.ao.models import *
import broadcast
from otalo.surveys import tasks as surveytasks

BCAST_BUFFER_SECS = 0 * 60
BACKUP_THRESH_MINS = 30
SOUND_EXT = '.wav'

@shared_task
def thread(messageforum, template, subjects, responseprompt, num_backups, start_date, bcastname=None):
    line = messageforum.forum.line_set.all()[0]
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
    bcast = broadcast.clone_template(template, newname, num_backups, start_date)
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
    origpost = Prompt(file=messageforum.message.file.path, order=order, bargein=True, survey=bcast)
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
        
        responsecontent = Prompt(file=response.message.file.path, order=order, bargein=True, survey=bcast)
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

@shared_task
def regular_bcast(line, template, subjects, num_backups, start_date, bcastname=None):
    # create a clone from the template
    now = datetime.now()
    newname = bcastname
    if not newname or newname=='':
        newname = template.name.replace(Survey.TEMPLATE_DESIGNATOR, '') + '_' + datetime.strftime(now, '%b-%d-%Y')
    newname = newname[:128]
    bcast = broadcast.clone_template(template, newname, num_backups, start_date)
    for su in subjects:
        bcast.subjects.add(su)
    for d in line.dialers.all():
        bcast.dialers.add(d)
    
    print("Created regular bcast "+ str(bcast) + " time " + str(bcast.created_on))
    return bcast

'''
'    Helper function to run periodic tasks with the scheduler
'    Don't run as a subtask since it's just a helper
'''
@shared_task
def schedule_bcasts_by_dialers(dialerids):
    dialers = Dialer.objects.all()
    if dialerids:
        dialers = dialers.filter(pk__in=dialerids)
        
    schedule_bcasts(dialers=dialers)
    
'''
'    Helper function to run periodic tasks with the scheduler
'    Don't run as a subtask since it's just a helper
'''
@shared_task
def schedule_bcasts_by_basenums(numbers):
    dialers = Dialer.objects.filter(base_number__in=numbers)
    
    schedule_bcasts(dialers=dialers)
    
'''
'    A periodic task that gets surveys and creates
'    calls. Why periodic? Because we need to run the scheduling
'    algorithm on calls to prioritize which go out first between bcasts
'    over a given dialer.
'
'    Doing it here higher up in the app logic to keep the actual
'    dialer tasks as pure and simple as possible. Assume nothing
'    about how calls should go out, just send them out.
'''
@shared_task
def schedule_bcasts(time=None, dialers=None):
    # gather all bcasts pending as of bcasttime
    # This is a comparison between group recipients and calls scheduled
    if not dialers:
        dialers = Dialer.objects.all()
    
    for dialer in dialers:
        bcasttime = time
        if bcasttime is None:
            bcasttime = datetime.now()
            
        print("Scheduling bcasts for dialer " + str(dialer) + "-" + broadcast.date_str(bcasttime))
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
        nums = broadcast.get_dialer_numbers(dialer)
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
                to_sched = broadcast.get_pending_backup_calls(bcast, num_backup_calls)
                
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
                
            surveytasks.schedule_call.s().set(countdown=BCAST_BUFFER_SECS).delay(survey, dialer, subject, priority)
            #surveytasks.test_task.s().delay(survey, dialer, subject, priority, bcasttime)
            num_scheduled += 1
