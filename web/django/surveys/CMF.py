'''
    Copyright (c) 2009 Regents of the University of California, Stanford University, and others
 
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
 
        http://www.apache.org/licenses/LICENSE-2.0
 
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

import sys, csv
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Sum
from otalo.ao.models import Line, User, Message_forum
from otalo.surveys.models import Survey, Prompt, Option, Call, Input, Subject
import otalo_utils, call_duration

CMF_DESIGNATOR = '_CMF'
CMF_OUTPUT_DIR = '/home/cmf/reports/'
#CMF_OUTPUT_DIR = ''
SUBDIR = 'guj/cmf/'
SOUND_EXT = '.wav'
AO2_NUMBER = '7930142013'

def add_users(names, numbers, villages, treatment_group):
    added = 0
    modified = 0
    for i in range(len(numbers)):
        number = numbers[i]
        user = User.objects.filter(number=number)
        if bool(user):
            user = user[0]
            user.allowed = 'y'
            user.indirect_bcasts_allowed = False
            if user.name is None or CMF_DESIGNATOR not in user.name:
                user.name = names[i] + CMF_DESIGNATOR
            user.village = villages[i]
            if number in treatment_group:
                print('found treatment num')
                user.balance = -1
            user.save()
            print("modified "+ str(user))
            modified += 1
        else:
            user = User(number=number, name=names[i]+CMF_DESIGNATOR, village=villages[i], allowed='y', indirect_bcasts_allowed=False)
            if number in treatment_group:
                print('found treatment num')
                user.balance = -1
            user.save()
            print("added "+ str(user))
            added += 1
            
    print(str(added)+" users added; "+str(modified)+" users modified")
    
def get_numbers(f):
    f = open(f)
    numbers = []
    while(True):
        num = f.readline()
        if not num:
            break
        numbers.append(num.strip())
        
    return numbers

def date_str(date):
    #return date.strftime('%Y-%m-%d')
    return date.strftime('%m-%d-%y')

def time_str(date):
    #return date.strftime('%Y-%m-%d')
    return date.strftime('%m-%d-%y %H:%M')

'''
****************************************************************************
******************* SURVEY GENERATION ****************************************
****************************************************************************
'''

def create_survey(num, prefix, suffix):
    s = Survey.objects.filter(name__contains='CMF_SURVEY', number=num, template=True)
    if bool(s):
        s[0].delete()
    s = Survey(name='CMF_SURVEY', template=True, number=num, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0)
    s.save()    
    order = 1
    
    welcome = Prompt(file=SUBDIR+"welcome"+SOUND_EXT, order=order, bargein=False, survey=s, delay=0)
    welcome.save()
    welcome_opt = Option(number="", action=Option.NEXT, prompt=welcome)
    welcome_opt.save()
    order+=1
    
    q1 = Prompt(file=SUBDIR+"q1"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
    q1.save()
    q1_opt = Option(number="1", action=Option.INPUT, prompt=q1)
    q1_opt.save()
    q1_opt2 = Option(number="2", action=Option.INPUT, prompt=q1)
    q1_opt2.save()
    q1_opt3 = Option(number="3", action=Option.INPUT, prompt=q1)
    q1_opt3.save()
    q1_opt4 = Option(number="4", action=Option.INPUT, prompt=q1)
    q1_opt4.save()
    order+= 1
    
    q2 = Prompt(file=SUBDIR+"q2"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
    q2.save()
    q2_opt = Option(number="1", action=Option.INPUT, prompt=q2)
    q2_opt.save()
    q2_opt2 = Option(number="2", action=Option.INPUT, prompt=q2)
    q2_opt2.save()
    q2_opt3 = Option(number="3", action=Option.INPUT, prompt=q2)
    q2_opt3.save()
    q2_opt4 = Option(number="4", action=Option.INPUT, prompt=q2)
    q2_opt4.save()
    order += 1
    
    '''
    q3 = Prompt(file=SUBDIR+"q3"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
    q3.save()
    q3_opt = Option(number="1", action=Option.INPUT, prompt=q3)
    q3_opt.save()
    q3_opt2 = Option(number="2", action=Option.INPUT, prompt=q3)
    q3_opt2.save()
    q3_opt3 = Option(number="3", action=Option.INPUT, prompt=q3)
    q3_opt3.save()
    q3_opt4 = Option(number="4", action=Option.INPUT, prompt=q3)
    q3_opt4.save()
    order+=1
    '''
    
    thankyou = Prompt(file=SUBDIR+"thankyou"+SOUND_EXT, order=order, bargein=False, survey=s, delay=0)
    thankyou.save()
    thankyou_opt = Option(number="", action=Option.NEXT, prompt=thankyou)
    thankyou_opt.save()
    order+=1
        
    return s

def create_blank(num, prefix, suffix):
    s = Survey.objects.filter(name__contains='BLANK', number=num, template=True)
    if not bool(s):
        s = Survey(name='BLANK', template=True, number=num, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0)
        s.save()    
        
        blank = Prompt(file='guj/blank.wav', order=1, bargein=False, survey=s, delay=0)
        blank.save()
        blank_opt = Option(number="", action=Option.NEXT, prompt=blank)
        blank_opt.save()
        
        return s
    
def create_template(line, title, pre, post):
    name = title
    
    s = Survey.objects.filter(name=name)
    if not bool(s):
        s = Survey(name=name, complete_after=0, number=line.outbound_number or line.number, template=True)
        print ("adding template " + str(s))
        s.save()
    
        # pre
        welcome = Prompt.objects.create(file=language+"/pre"+SOUND_EXT, order=1, bargein=True, survey=s)
        welcome_opt1 = Option.objects.create(number="", action=Option.NEXT, prompt=welcome)
        welcome_opt9 = Option.objects.create(number="9", action=Option.NEXT, prompt=welcome)
        
        # post
        thanks = Prompt.objects.create(file=language+"/post"+SOUND_EXT, order=3, bargein=False, survey=s)
        thanks_opt1 = Option.objects.create(number="", action=Option.NEXT, prompt=thanks)
        
        return s
    else:
        return s[0]

'''
****************************************************************************
******************* REPORTING **********************************************
****************************************************************************
'''

def get_features_within_call(number, feature_list, filename, date_start=False, date_end=False, delim=','):
    all_calls = []
    open_calls = {}
    
    f = open(filename)
    
    while(True):
        line = f.readline()
        if not line:
            break
        try:
        
        #################################################
        ## Use the calls here to determine what pieces
        ## of data must exist for the line to be valid.
        ## All of those below should probably always be.
        
            phone_num = otalo_utils.get_phone_num(line)
            current_date = otalo_utils.get_date(line)        
            dest = otalo_utils.get_destination(line)            
        ##
        ################################################
                
            if date_start:
                if date_end:
                    if not (current_date >= date_start and current_date < date_end):
                        continue
                    if current_date > date_end:
                        break
                else:
                    if not current_date >= date_start:
                        continue
    
            if line.find("Start call") != -1:
                # check to see if this caller already has one open
                if phone_num in open_calls:
                    # close out current call
                    call = open_calls[phone_num]    
                    dur = current_date - call['start']
                    # may not be there if it's an old number
                    treatment = 'N/A'
                    u = User.objects.filter(number=phone_num)
                    if bool(u):
                        u = u[0]
                        treatment = 'No'
                        if u.balance == -1:
                            treatment = 'Yes'
                    call_info = [phone_num,treatment,date_str(call['start']),str(dur.seconds)]
                    for feature in feature_list:
                        if feature in call:
                            call_info.append(call[feature])
                        else:
                            call_info.append('')
                    
                    all_calls.append(call_info)
                    del open_calls[phone_num]
                    
                # add new call
                #print("adding new call: " + phone_num)
                open_calls[phone_num] = {'order':'','feature_chosen':False,'start':current_date,'last':current_date}
                
            elif line.find("End call") != -1:
                if phone_num in open_calls:
                    # close out call                
                    call = open_calls[phone_num]
                    dur = current_date - call['start']
                    # may not be there if it's an old number
                    treatment = 'N/A'
                    u = User.objects.filter(number=phone_num)
                    if bool(u):
                        u = u[0]
                        treatment = 'No'
                        if u.balance == -1:
                            treatment = 'Yes'
                    call_info = [phone_num,treatment,date_str(call['start']),str(dur.seconds)]
                    for feature in feature_list:
                        if feature in call:
                            call_info.append(call[feature])
                        else:
                            call_info.append('')
                    
                    all_calls.append(call_info)
                    del open_calls[phone_num]
            elif phone_num in open_calls:
                call = open_calls[phone_num]
                feature = line[line.rfind('/')+1:line.find('.wav')]
                if feature == "okyourreplies" or feature == "okplay_all" or feature == "okplay" or feature == "okrecord":
                    if feature in call:
                        call[feature] += 1
                    else:
                        call[feature] = 1
                    call['order'] += feature+','
                elif feature == "okyouwant_pre" or feature == "okplaytag_pre":
                    # on the next go-around, look for the feature
                    call['feature_chosen'] = True
                elif call['feature_chosen']:
                    if feature in call:
                        call[feature] += 1
                    else:
                        call[feature] = 1
                    call['order'] += feature+','
                    call['feature_chosen'] = False
                
                call['last'] = current_date
                    
        except KeyError as err:
            #print("KeyError: " + phone_num + "-" + otalo.date_str(current_date))
            raise
        except ValueError as err:
            #print("ValueError: " + line)
            continue
        except IndexError as err:
            continue
        except otalo_utils.PhoneNumException:
            #print("PhoneNumException: " + line)
            continue
        
    header = ['number','treatment?','date','duration'] + feature_list
    if date_start:
        outfilename='features_'+number[-8:]+'_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]+'.csv'
    else:
        outfilename='features_'+number[-8:]+'.csv'
    outfilename = CMF_OUTPUT_DIR+outfilename
    output = csv.writer(open(outfilename, 'wb'))
    output.writerow(header)
    output.writerows(all_calls)
    
def get_broadcast_calls(number, filename, date_start=None, date_end=None):
    all_calls = []
    open_calls = {}
    
    f = open(filename)

    while(True):
        line = f.readline()
        if not line:
            break
        try:
        
        #################################################
        ## Use the calls here to determine what pieces
        ## of data must exist for the line to be valid.
        ## All of those below should probably always be.
        
            phone_num = otalo_utils.get_phone_num(line)
            current_date = otalo_utils.get_date(line)        
            dest = otalo_utils.get_destination(line)            
        ##
        ################################################
                
            if date_start:
                if date_end:
                    if not (current_date >= date_start and current_date < date_end):
                        continue
                    if current_date > date_end:
                        break
                else:
                    if not current_date >= date_start:
                        continue
    
            if line.find("Start call") != -1:
                # check to see if this caller already has one open
                if phone_num in open_calls:
                    # close out current call
                    call = open_calls[phone_num]    
                    start = call['start']
                    dur = current_date - start
                    # may not be there if it's an old number
                    treatment = 'N/A'
                    uname = ''
                    u = User.objects.filter(number=phone_num)
                    if bool(u):
                        u = u[0]
                        treatment = 'No'
                        uname = u.name
                        if u.balance == -1:
                            treatment = 'Yes'
                    last_prompt_file = call['last_prompt']
                    call = Call.objects.filter(subject__number=phone_num, date__year=start.year, date__month=start.month, date__day=start.day, complete=True, survey__broadcast=True)
                    if bool(call):
                        call = call[0]
                        priority = str(call.priority)
                        input = Input.objects.filter(call=call)
                        if input:
                            input = input[0].input
                        else:
                            input = 'N/A'                          
                        #all_calls += phone_num+delim+priority+delim+time_str(start)+delim+str(dur.seconds)+"\n"
                        all_calls.append([uname, treatment,priority,time_str(start),str(dur.seconds), last_prompt_file, input])                        
                    del open_calls[phone_num]
                    
                # add new call
                #print("adding new call: " + phone_num)
                open_calls[phone_num] = {'start':current_date, 'last_prompt':'Start Call'}
                
            elif line.find("End call") != -1:
                if phone_num in open_calls:
                    # close out call                
                    call = open_calls[phone_num]    
                    start = call['start']
                    dur = current_date - start
                    # may not be there if it's an old number
                    treatment = 'N/A'
                    uname = ''
                    u = User.objects.filter(number=phone_num)
                    if bool(u):
                        u = u[0]
                        treatment = 'No'
                        uname = u.name
                        if u.balance == -1:
                            treatment = 'Yes'
                    last_prompt_file = call['last_prompt']
                    call = Call.objects.filter(subject__number=phone_num, date__year=start.year, date__month=start.month, date__day=start.day, complete=True, survey__broadcast=True)
                    if bool(call):
                        call = call[0]
                        priority = str(call.priority)
                        input = Input.objects.filter(call=call)
                        if input:
                            input = input[0].input
                        else:
                            input = 'N/A'                         
                        #all_calls += phone_num+delim+priority+delim+time_str(start)+delim+str(dur.seconds)+"\n"
                        all_calls.append([uname,treatment,priority,time_str(start),str(dur.seconds), last_prompt_file, input])
                    del open_calls[phone_num]
                    
            elif phone_num in open_calls:
                call = open_calls[phone_num]
                prompt = line[line.rfind('/')+1:]
                call['last_prompt'] = prompt.strip()
                    
        except KeyError as err:
            #print("KeyError: " + phone_num + "-" + otalo.date_str(current_date))
            raise
        except ValueError as err:
            #print("ValueError: " + line)
            continue
        except IndexError as err:
            continue
        except otalo_utils.PhoneNumException:
            #print("PhoneNumException: " + line)
            continue
                
    header = ['name','treatment?','call try #','time','duration','last prompt','input']    
    if date_start:
        outfilename='outgoing_'+number[-8:]+'_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]+'.csv'
    else:
        outfilename='outgoing_'+number[-8:]+'.csv'
    outfilename = CMF_OUTPUT_DIR+outfilename
    output = csv.writer(open(outfilename, 'wb'))
    output.writerow(header)
    output.writerows(all_calls)
    nocalls=[]
    for num in phone_num_filter:
        #print('number is ' + num)
        calls = Call.objects.select_related().filter(subject__number=num, survey__broadcast=True)
        #print('got calls')
        calls_by_survey = {}
        for call in calls:
            if date_end and call.priority == 1 and call.date > date_end:
                break
            s = call.survey
            if s in calls_by_survey:
                calls_by_survey[s].append(call)
            elif call.priority == 1:
                if date_start:
                    if call.date >= date_start:
                        calls_by_survey[s] = [call]
                else:
                    calls_by_survey[s] = [call]
        for survey,calls in calls_by_survey.items():
            #print('processing survey ' + str(survey))
            complete = filter(lambda call: call.complete==True, calls)
            if not(bool(complete)):
                #print('getting first att call for survey ' + str(survey.id) + ' number '+ num)
                first_call = filter(lambda call: call.priority==1, calls)[0]
                first_att = first_call.date
                
                # may not be there if it's an old number
                treatment = 'N/A'
                u = User.objects.filter(number=phone_num)
                if bool(u):
                    u = u[0]
                    treatment = 'No'
                    if u.balance == -1:
                        treatment = 'Yes'
                nocalls.append([num,treatment,'1',time_str(first_att),'N/A','N/A','N/A'])
    output.writerows(nocalls)

def get_broadcast_calls2(line, date_start=None, date_end=None):
    all_calls = []
    number = line.outbound_number or line.number
    
    calls = Call.objects.filter(survey__number=outbound_num, survey__broadcast=True, complete=True)
    surveys = Survey.objects.filter(number=number, broadcast=True).order_by('created_on')
    if date_start:
        surveys = surveys.filter(created_on__gte=date_start)
    if date_end:
        surveys = surveys.filter(created_on__lt=date_end)
        
    for survey in surveys:
        calls = Call.objects.filter(survey=survey, complete=True)
        completed = {}
        for call in calls:
            completed[call.subject]=call
            
        for subject in survey.subjects.all():            
            name = subject.number
            u = User.objects.filter(number=subject.number)
            if bool(u):
                u=u[0]
                if u.name and u.name != '':
                    name = u.name
            result = [name]
            if subject in completed:
                call = completed[subject]
                result += [call.priority, time_str(call.date), call.duration]
                for input in Input.objects.filter(call=call):
                    result.append(input.input)
            else:
                result += ['N/A', 'N/A', 'N/A', 'N/A']
            
            all_calls.append(result)
                
    header = ['name','call try #','time','duration','input(s)']    
    if date_start:
        outfilename='outgoing_'+number[-8:]+'_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]+'.csv'
    else:
        outfilename='outgoing_'+number[-8:]+'.csv'
    outfilename = CMF_OUTPUT_DIR+outfilename
    output = csv.writer(open(outfilename, 'wb'))
    output.writerow(header)
    output.writerows(all_calls)
    
def get_message_listens(number, filename, date_start=False, date_end=False, transfer_calls=False, delim=','):
    all_calls = []
    open_calls = {}
    
    f = open(filename)
    while(True):
        line = f.readline()
        if not line:
            break
        try:
        
        #################################################
        ## Use the calls here to determine what pieces
        ## of data must exist for the line to be valid.
        ## All of those below should probably always be.
        
            phone_num = otalo_utils.get_phone_num(line)
            current_date = otalo_utils.get_date(line)        
            dest = otalo_utils.get_destination(line)            
        ##
        ################################################
                
            if date_start:
                if date_end:
                    if not (current_date >= date_start and current_date < date_end):
                        continue
                    if current_date > date_end:
                        break
                else:
                    if not current_date >= date_start:
                        continue
            
            # A hacky way to test for transfer call
            # In the future you want to compare this call's
            # start time to a time window related to the end
            # of the survey call (in which you can keep the flag
            # false and give a more targeted start and end date)
            if transfer_calls:
                if transfer_calls == "INBOUND_ONLY" and len(dest) == 10:
                    continue
                elif transfer_calls == "TRANSFER_ONLY" and len(dest) < 10:
                    continue
                
            if line.find("Start call") != -1:
                # check to see if this caller already has one open
                if phone_num in open_calls:
                    # close out current call
                    del open_calls[phone_num]
                    
                # add new call
                #print("adding new call: " + phone_num)
                open_calls[phone_num] = False
                
            elif line.find("End call") != -1:
                if phone_num in open_calls:
                    # close out call                
                    del open_calls[phone_num]
            
            if phone_num in open_calls:  
                if line.find("Stream") != -1:
                    fname = line[line.rfind('/')+1:].strip()
                    open_calls[phone_num] = [fname, current_date]
                elif open_calls[phone_num]:
                    fname = open_calls[phone_num][0]
                    listenstart = open_calls[phone_num][1]
                    sessid = otalo_utils.get_sessid(line)
                    # may not be there if it's an old number
                    treatment = 'N/A'
                    uid = 'N/A'
                    uname = 'N/A'
                    u = User.objects.filter(number=phone_num)
                    if bool(u):
                        u = u[0]
                        uid = str(u.id)
                        uname = u.name
                        treatment = 'No'
                        if u.balance == -1:
                            treatment = 'Yes'
                    mf = Message_forum.objects.get(message__file__contains=fname)
                    tags = [t.tag for t in mf.tags.all()]
                    dur = (current_date-listenstart).seconds
                    all_calls.append([uid,treatment,sessid,str(listenstart),uname,str(mf.forum.id),str(mf.id),str(mf.message.date),str(dur)]+tags)
                    
                    open_calls[phone_num] = False
                
            
        except KeyError as err:
            #print("KeyError: " + phone_num + "-" + otalo.date_str(current_date))
            raise
        except ValueError as err:
            #print("ValueError: " + line)
            continue
        except IndexError as err:
            #print("IndexError: " + line)
            continue
        except otalo_utils.PhoneNumException:
            #print("PhoneNumException: " + line)
            continue
    
    header = ['UserId','Treatment?','SessId','ListenTime','Name','ForumId','MessageForumId','MessageDate','ListenDuration(s)','Tags']
    if date_start:
        outfilename='listens_'+number[-8:]+'_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]+'.csv'
    else:
        outfilename='listens_'+number[-8:]+'.csv'
    outfilename = CMF_OUTPUT_DIR+outfilename
    output = csv.writer(open(outfilename, 'wb'))
    output.writerow(header)
    output.writerows(all_calls)

def get_survey_results(phone_num_filter, date_start=False, date_end=False):
    # get surveys
    surveys = Survey.objects.filter(broadcast=True, name__contains='CMF_SURVEY')
    calls = Call.objects.filter(survey__in=surveys, complete=True)
    
    if date_start:
        calls = calls.filter(date__gte=date_start)
        
    if date_end:
        calls = calls.filter(date__lt=date_end)
    
    header = ['UserNum', 'time', 'Q1', 'Q2', 'Q3']
    results = [header]
    for call in calls:
        inputs = Input.objects.select_related(depth=1).filter(call=call)
        inputs = [input for input in inputs]
        result = [call.subject.number, time_str(call.date)]
        q1 = filter(lambda input: 'q1' in input.prompt.file, inputs)
        if bool(q1):
            result.append(q1[0].input)
        q2 = filter(lambda input: 'q2' in input.prompt.file, inputs)
        if bool(q2):
            result.append(q2[0].input)
        q3 = filter(lambda input: 'q3' in input.prompt.file, inputs)
        if bool(q3):
            result.append(q3[0].input)
        results.append(result)
    
    if date_start:
        outfilename='survey_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]+'.csv'
    else:
        outfilename='survey.csv'
        
    outfilename = CMF_OUTPUT_DIR+outfilename
    output = csv.writer(open(outfilename, 'wb'))
    output.writerows(results)
    nocalls = []
    for num in phone_num_filter:
        #print('number is ' + num)
        calls = Call.objects.select_related().filter(subject__number=num, survey__in=surveys)
        #print('got calls')
        calls_by_survey = {}
        for call in calls:
            if date_end and call.priority == 1 and call.date > date_end:
                break
            s = call.survey
            if s in calls_by_survey:
                calls_by_survey[s].append(call)
            elif call.priority == 1:
                if date_start:
                    if call.date >= date_start:
                        calls_by_survey[s] = [call]
                else:
                    calls_by_survey[s] = [call]
        for survey,calls in calls_by_survey.items():
            #print('processing survey ' + str(survey))
            complete = filter(lambda call: call.complete==True, calls)
            if not(bool(complete)):
                #print('getting first att call for survey ' + str(survey.id) + ' number '+ num)
                first_call = filter(lambda call: call.priority==1, calls)[0]
                first_att = first_call.date
                
                nocalls.append([num,time_str(first_att),'N/A','N/A','N/A'])
    output.writerows(nocalls)

def get_broadcast_minutes(line, date_start=None, date_end=None):
    all_surveys = []
    number = line.outbound_number or line.number
    
    calls = Call.objects.filter(survey__number=outbound_num, survey__broadcast=True, complete=True)
    surveys = Survey.objects.filter(number=number, broadcast=True).order_by('created_on')
    if date_start:
        surveys = surveys.filter(created_on__gte=date_start)
    if date_end:
        surveys = surveys.filter(created_on__lt=date_end)
        
    for survey in surveys:
        attempts = Call.objects.filter(survey=survey).count()
        recipients = survey.subjects.all().count()
        completed = Call.objects.filter(survey=survey, complete=True).count()
        secs = Call.objects.filter(survey=survey, complete=True).aggregate(Sum('duration'))
        secs = secs.values()[0]
        mins = 0
        if secs:
            mins = secs / 60
        all_surveys.append([survey.id,survey.name,time_str(survey.created_on),recipients,attempts,completed,mins])
        
    header = ['surveyid','survey name','start','num recipients','attempts','completed','total mins']    
    if date_start:
        outfilename='bcast_minutes_'+number[-8:]+'_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]+'.csv'
    else:
        outfilename='bcast_minutes'+number[-8:]+'.csv'
    outfilename = CMF_OUTPUT_DIR+outfilename
    output = csv.writer(open(outfilename, 'wb'))
    output.writerow(header)
    output.writerows(all_surveys)

def get_message_topics(forumids, phone_num_filter=False, date_start=False, date_end=False):
    msgs = Message_forum.objects.filter(forum__in=forumids)
    if phone_num_filter:
        msgs = msgs.filter(message__user__number__in=phone_num_filter)
    if date_start:
        msgs = msgs.filter(message__date__gte=date_start) 
    if date_end:
        msgs = msgs.filter(message__date__lt=date_end)
        
    header = ['phone num','message time','forum','tags']    
    if date_start:
        outfilename='message_topics_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]+'.csv'
    else:
        outfilename='message_topics.csv'
    outfilename = CMF_OUTPUT_DIR+outfilename
    output = csv.writer(open(outfilename, 'wb'))
    output.writerow(header)
    for mf in msgs:
        tags = [t.tag for t in mf.tags.all()]
                
        output.writerow([mf.message.user.number, time_str(mf.message.date), mf.forum.name]+tags)
    
def get_minutes_used(aoline, inboundf, date_start=None, date_end=None):
    # Get AO1 minutes used
    inbound = call_duration.get_online_time(inboundf, date_start=date_start, date_end=date_end, quiet=True)
    aoinbound = 0
    for date in inbound:
        aoinbound += inbound[date]
    if aoinbound:
        aoinbound = aoinbound / 60
        
    # broadcast
    out_num = aoline.outbound_number or aoline.number
    aooutbound = Call.objects.filter(survey__number=out_num)
    if date_start:
        aooutbound = aooutbound.filter(date__gt=date_start)
    if date_end:
        aooutbound = aooutbound.filter(date__lte=date_end)
    aooutbound = aooutbound.aggregate(Sum('duration'))
    aooutbound = aooutbound.values()[0]
    if aooutbound:
        aooutbound = aooutbound / 60
        
    # Get AO2 minutes used
    # inbound
    line = Line.objects.get(number=AO2_NUMBER)
    lineid = str(line.id)
    inboundf = settings.INBOUND_LOG_ROOT + lineid + '.log'
    out_num = line.outbound_number or line.number
    
    inbound = call_duration.get_online_time(inboundf, date_start=date_start, date_end=date_end, quiet=True)
    ao2inbound = 0
    for date in inbound:
        ao2inbound += inbound[date]
    if ao2inbound:
        ao2inbound = ao2inbound / 60
        
    # broadcast
    ao2outbound = Call.objects.filter(survey__number=out_num)
    if date_start:
        ao2outbound = ao2outbound.filter(date__gt=date_start)
    if date_end:
        ao2outbound = ao2outbound.filter(date__lte=date_end)
    ao2outbound = ao2outbound.aggregate(Sum('duration'))
    ao2outbound = ao2outbound.values()[0]
    if ao2outbound:
        ao2outbound = ao2outbound / 60
    
    if not date_start:
        date_start = inbound[0]
        
    if not date_end:
        date_end = datetime.now()
         
    # prepare email
    print("<html>")
    print("<div> Below are minutes used on AO and AO2 between " + date_str(date_start) + " and " + date_str(date_end) + "</div>")
    print("<br/><div>")
    print("<b>AO minutes:</b> ")
    print(str(aoinbound))
    print(" inbound; ")
    print(str(aooutbound))
    print(" outbound")
    print("</div>")
    
    print("<br/><div>")
    print("<b>AO2 minutes:</b> ")
    print(str(ao2inbound))
    print(" inbound; ")
    print(str(ao2outbound))
    print(" outbound")
    print("</div>")
    
    print("</html>")
    
def responder_report(userid, forumids, date_start=False, date_end=False, ):
    responder = User.objects.get(pk=userid)
    responses = Message_forum.objects.filter(message__user=responder, forum__in=forumids, status=Message_forum.STATUS_APPROVED, message__rgt__gt=1)
    if date_start:
        responses = responses.filter(message__date__gte=date_start)
    if date_end:
        responses = responses.filter(message__date__lt=date_end)
    
    print("Responses for " + responder.name)
    print("Message ID\tMessage Date\tForum")
    messagecnt = 0
    for response in responses:
        print(str(response.id)+"\t"+date_str(response.message.date)+"\t"+response.forum.name)
        messagecnt += 1
    print("Total: "+ str(messagecnt))
    
    
'''
****************************************************************************
******************* UTILS **************************************************
****************************************************************************
''' 
def date_str(date):
    #return date.strftime('%Y-%m-%d')
    return date.strftime('%b-%d-%y')

'''
****************************************************************************
******************* MAIN ***************************************************
****************************************************************************
''' 
def main():

    lineid = sys.argv[2]
    line = Line.objects.get(pk=lineid)
        
    now = datetime.now()
    today = datetime(year=now.year, month=now.month, day=now.day)
        
    inbound = settings.INBOUND_LOG_ROOT + lineid + '.log'
    out_num = line.outbound_number or line.number
    outbound = settings.OUTBOUND_LOG_ROOT + out_num + '.log'
    
    if '--report' in sys.argv:
        startdate = None
        enddate = None
        features = sys.argv[3].split(',')
        
        if len(sys.argv) > 4:
            startdate = datetime.strptime(sys.argv[4], "%m-%d-%Y")
        else:
            startdate = today-timedelta(days=7)
        if len(sys.argv) > 5:
            enddate = datetime.strptime(sys.argv[5], "%m-%d-%Y")
        
        features=['qna', 'announcements', 'radio', 'experiences', 'okyourreplies', 'okrecord', 'okplay', 'okplay_all', 'cotton', 'wheat', 'cumin', 'castor']
        get_features_within_call(line.number, features, inbound, date_start=startdate, date_end=enddate)
        get_broadcast_calls(line, date_start=startdate, date_end=enddate)
        get_message_listens(line.number, inbound, date_start=startdate, date_end=enddate)
        get_broadcast_minutes(line, date_start=startdate, date_end=enddate)
    elif '--usageemail' in sys.argv:
        if len(sys.argv) > 3:
            usagestart = datetime.strptime(sys.argv[3], "%m-%d-%Y")
        else:
            # set to last 15th
            if today.day > 15:
                usagestart = datetime(year=today.year, month=today.month, day=15)
            else:
                year = today.year
                month = today.month - 1
                if today.month == 1:
                    year = today.year - 1
                    month = 12
                usagestart = datetime(year=year, month=month, day=15)
                
        usageend=None
        if len(sys.argv) > 4:
            usageend = datetime.strptime(sys.argv[4], "%m-%d-%Y")
            
        get_minutes_used(line, inbound, date_start=usagestart, date_end=usageend)

    #get_message_topics([1,2], numbers, date_start=startdate, date_end=enddate)
    #num = line.outbound_number
    #if not num:
    #   num = line.number
    #num = '7930142011'
    #create_survey(num, line.dialstring_prefix, line.dialstring_suffix)
    #create_blank(num, line.dialstring_prefix, line.dialstring_suffix)
    #get_survey_results()
    
    #responder_report(48, [1], date_start=datetime(year=2012, month=1, day=1))
    
main()
