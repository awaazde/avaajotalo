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
import sys, os, csv
from datetime import datetime, timedelta
from django.conf import settings
from otalo.ao.models import Line, User, Forum, Message_forum, Tag, Forum_tag
from otalo.surveys.models import Survey, Subject, Call, Prompt, Option, Param, Input
import otalo_utils, num_calls

'''
****************************************************************************
******************* CONSTANTS **********************************************
****************************************************************************
'''
LINEID=16
OUTPUT_FILE_DIR='/home/galli/reports/'
SOUND_EXT = ".wav"

'''
****************************************************************************
******************* SURVEY GENERATION **************************************
****************************************************************************
'''

def standard_template(line, contenttype):
    prefix = line.dialstring_prefix
    suffix = line.dialstring_suffix
    language = line.language
    if line.outbound_number:
        number = line.outbound_number
    else:
        number = line.number
    
    name = contenttype
    s = Survey.objects.filter(name=name, number=number, template=True)
    if bool(s):
        s = s[0]
        s.delete()
        print('deleting survey')
    s = Survey(name=name, number=number, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0, template=True)
    s.save()
    print('creating new survey '+str(s))
    
    # welcome
    welcome = Prompt(file=language+"/welcome_"+contenttype+SOUND_EXT, order=1, bargein=True, survey=s, delay=0)
    welcome.save()
    welcome_opt1 = Option(number="", action=Option.NEXT, prompt=welcome)
    welcome_opt1.save()
    welcome_opt2 = Option(number="1", action=Option.NEXT, prompt=welcome)
    welcome_opt2.save()
    
    # content
#        content = Prompt(file=language+"/"+contenttype+SOUND_EXT, order=2, bargein=True, survey=s)
#        content.save()
#        content_opt = Option(number="", action=Option.NEXT, prompt=content)
#        content_opt.save()
#        content_opt2 = Option(number="1", action=Option.NEXT, prompt=content)
#        content_opt2.save()
    
    # thanks
    thanks = Prompt(file=language+"/thankyou_"+contenttype+SOUND_EXT, order=3, bargein=True, survey=s)
    thanks.save()
    thanks_opt1 = Option(number="", action=Option.NEXT, prompt=thanks)
    thanks_opt1.save()
    thanks_opt2 = Option(number="9", action=Option.PREV, prompt=thanks)
    thanks_opt2.save()
        
    return s
    
def monitoring_template(line, questionname):
    prefix = line.dialstring_prefix
    suffix = line.dialstring_suffix
    language = line.language
    if line.outbound_number:
        number = line.outbound_number
    else:
        number = line.number
    
    s = Survey.objects.filter(name=questionname, number=number, template=True)
    if bool(s):
        s = s[0]
        s.delete()
        print('deleting survey')
    s = Survey(name=questionname, number=number, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0, template=True)
    s.save()
    print('creating new survey '+str(s))
    
    welcome = Prompt(file=language+"/MFQw-guj"+SOUND_EXT, order=1, bargein=True, survey=s, delay=0)
    welcome.save()
    welcome_opt1 = Option(number="", action=Option.NEXT, prompt=welcome)
    welcome_opt1.save()
      
    question = Prompt(file=language+"/"+questionname+SOUND_EXT, order=2, bargein=True, survey=s, delay=4000)
    question.save()
    question_opt1 = Option(number="1", action=Option.INPUT, prompt=question)
    question_opt1.save()
    question_opt2 = Option(number="2", action=Option.INPUT, prompt=question)
    question_opt2.save()
    question_opt3 = Option(number="3", action=Option.INPUT, prompt=question)
    question_opt3.save()
    question_opt4 = Option(number="4", action=Option.INPUT, prompt=question)
    question_opt4.save()
        
    thanks = Prompt(file=language+"/MFQe-guj"+SOUND_EXT, order=3, bargein=True, survey=s)
    thanks.save()
    thanks_opt1 = Option(number="", action=Option.NEXT, prompt=thanks)
    thanks_opt1.save()
    
    return s

'''
****************************************************************************
******************* REPORTING **********************************************
****************************************************************************
'''
        
def monitoring_results(number, phone_num_filter=False, date_start=False, date_end=False):
    all_calls = []
    questions = set()
    calls = Call.objects.filter(survey__number=number, survey__broadcast=True, complete=True)
    if phone_num_filter:
        calls = calls.filter(subject__number__in=phone_num_filter)
    if date_start:
        calls = calls.filter(date__gte=date_start)
    if date_end:
        calls = calls.filter(date__lt=date_end)
        
    for call in calls:
        user = User.objects.filter(number=call.subject.number)
        if bool(user):
            user = user[0]
            result = [user.name or '', user.number, user.taluka or '', user.village or '', time_str(call.date), call.duration or '']
        else:
            result = ['', call.subject.number, '', '', time_str(call.date), call.duration or '']
        
        inputs = Input.objects.select_related(depth=1).filter(call=call).order_by('id')
        
        for input in inputs:
            result.append(input.input)
            prompt = input.prompt
            questions.add(prompt.file[prompt.file.rfind('/')+1:prompt.file.find(SOUND_EXT)])                        
        all_calls.append(result)
        
    header = ['Name','Mobile Number', 'Code No', 'Village', 'Call start','Duration (s)']
    question = 'Response'
    if len(questions) == 1:
        question = list(questions)[0]
    header.append(question)
    outputfilename='monitoring_results_'+number
    if date_start:
        outputfilename+='_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]
    outputfilename = OUTPUT_FILE_DIR+outputfilename+'.csv'
    output = csv.writer(open(outputfilename, 'wb'))
    output.writerow(header)            
    output.writerows(all_calls)

def results_by_callee(linenumber, callees, date_start=None, date_end=None):
    # get calls
    calls = Call.objects.select_related().filter(survey__number=linenumber, complete=True, survey__broadcast=True, survey__prompt__file__contains="MFQw")
    
    if date_start:
        calls = calls.filter(date__gte=date_start)
        
    if date_end:
        calls = calls.filter(date__lt=date_end)

    prompt_names = Prompt.objects.filter(survey__call__in=calls).exclude(file__contains='MFQw').exclude(file__contains='MFQe').values('file').distinct()
    prompt_names = [pair.values()[0] for pair in prompt_names]
    header = ['Name', 'Mobile Number', 'Code No']
    for pname in prompt_names:
        header.append(pname[pname.rfind('/')+1:pname.rfind(SOUND_EXT)])
    
    all_callees = [header]
    for number in callees.keys():
        inputs = Input.objects.select_related().filter(call__subject__number=number,prompt__file__in=prompt_names)
        input_map = {}
        for input in inputs:
            input_map[input.prompt.file]=input.input
        row = [get_name(number,callees), number, get_codenum(number,callees)]
        for pname in prompt_names:
            if pname in input_map:
                row.append(input_map[pname])
            else:
                row.append('')
        all_callees.append(row)
        
    outputfilename='results_by_callee_'+linenumber
    if date_start:
        outputfilename+='_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]
    outputfilename = OUTPUT_FILE_DIR+outputfilename+'.csv'
    output = csv.writer(open(outputfilename, 'wb'))           
    output.writerows(all_callees)
    
def monthly_calls(inboundf, number, date_start, date_end=False):
    calls={}
    
    if not date_end:
        date_end = datetime.now()
    
    # inbound calls
    inbound_calls = num_calls.get_calls(inboundf, date_start=date_start, date_end=date_end, quiet=True)
        
    d = datetime(day=1, month=date_start.month, year=date_start.year)
    
    while d < date_end:
        if d.month == 12:
            month_end = datetime(day=1,month=1,year=d.year+1)
        else:
            month_end = datetime(day=1,month=d.month+1,year=d.year)
            
        ninbound_calls = 0
        for week in inbound_calls:
            if week >= d and week < month_end:
                ninbound_calls += inbound_calls[week]
                
        noutbound_calls = Call.objects.filter(survey__number=number, complete=True, date__gte=d, date__lt=month_end).count()
        
        bcasts = Survey.objects.filter(number=number, broadcast=True, call__date__gte=d, call__date__lt=month_end).distinct()
        naow_bcasts = bcasts.filter(prompt__file__contains='AOW').count()
        nmonitor_bcasts = bcasts.filter(prompt__file__contains='MFQw-guj').count()
        
        calls[d] = [ninbound_calls, noutbound_calls, naow_bcasts, nmonitor_bcasts, bcasts.count()]
        d = month_end
    
    print('Month\tInbound\tOutbound\tAOW bcasts\tMonitoring bcasts\tTotal bcasts')
    dates = calls.keys()
    dates.sort()
    for date in dates:
        call_lst = calls[date]
        print(time_str(date) + '\t' + '\t'.join(map(str, call_lst)) )
        
def features_report(line_obj, feature_list, filename, phone_num_filter=False, date_start=False, date_end=False, delim=','):
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
            
            if phone_num_filter and not phone_num in phone_num_filter:
                continue
                
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
                    u = User.objects.filter(number=phone_num)
                    name=code=village = None
                    if bool(u):
                        u = u[0]
                        name = u.name or ''
                        code = u.taluka or ''
                        village = u.village or ''
                    call_info = [name, phone_num, code, village, time_str(call['start']),str(dur.seconds)]
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
                    u = User.objects.filter(number=phone_num)
                    name=code=village = None
                    if bool(u):
                        u = u[0]
                        name = u.name or ''
                        code = u.taluka or ''
                        village = u.village or ''
                    call_info = [name, phone_num, code, village, time_str(call['start']),str(dur.seconds)]
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
        
    header = ['Name', 'Number', 'Code No', 'Village', 'Date','Duration'] + feature_list
    outfilename='features_'+line_obj.number
    if date_start:
        outfilename+='_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]+'.csv'

    outfilename = OUTPUT_FILE_DIR+outfilename+'.csv'
    output = csv.writer(open(outfilename, 'wb'))
    output.writerow(header)
    output.writerows(all_calls)   

def messages(line, date_start=None, date_end=None, status=None, outputdir='.'):
    statuses  = dict(Message_forum.STATUSES)
    forums = Forum.objects.filter(line=line)
    results = []
    messages = Message_forum.objects.filter(forum__in=forums)
    if date_start:
        messages = messages.filter(message__date__gte=date_start)
    if date_end:
        messages = messages.filter(message__date__lt=date_end)
    if status:
        messages = messages.filter(status=status)
        
    for m in messages:
        user = m.message.user
        main = [time_str(m.message.date), user.name or '',user.number, m.forum.name, m.message.id, statuses[m.status]]
        tags = m.tags.all()
        for t in tags:
            main.append(t.tag)
        results.append(main)
    
    header = ['Date', 'Name', 'Number', 'Forum', 'Message ID', 'Status', 'Tag1', 'Tag2']
    outputfilename='messages_'+line.number
    if date_start:
        outputfilename+='_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]
    if outputdir[-1:] != '/':
        outputdir += '/'
    outputfilename = outputdir+outputfilename+'.csv'
    output = csv.writer(open(outputfilename, 'wb'))
    output.writerow(header)            
    output.writerows(results)
    
'''
****************************************************************************
******************* UTILS **************************************************
****************************************************************************
'''
def time_str(date):
    #return date.strftime('%Y-%m-%d')
    return date.strftime('%m-%d-%y %H:%M')

def get_callees_info(callee_filename):
    info = {}
    
    f = csv.reader(open(callee_filename, "rU"))
    
    for line in f:        
        try:
            num = get_number(line)
            info[num] = line
            #print('loading info ' + str(line) + ' for number '+num)
        except ValueError as err:
            #print("ValueError: " + line)
            continue
    
    #print(info)
    return info

def get_number(line):
    # get last 10 digits only
    num = line[0][-10:]
    return num

def get_name(number, callees_info):
    name = ''
    if number in callees_info:
        name = callees_info[number][1].strip()
    return name

def get_codenum(number, callees_info):
    groupid = ''
    if number in callees_info:
        groupid = callees_info[number][2].strip()
    return groupid

def get_village(number, callees_info):
    village = ''
    if number in callees_info:
        village = callees_info[number][3].strip()
    return village

def add_users(callee_filename):
    added = 0
    modified = 0
    f = csv.reader(open(callee_filename, "rU"))
    
    for line in f:    
        line = [elt.strip() for elt in line]
        number = line[0]
        user = User.objects.filter(number=number)
        if bool(user):
            user = user[0]
            user.allowed = 'y'
            user.indirect_bcasts_allowed = False
            user.name = line[1]
            user.taluka = line[2]
            user.village = line[3]
            user.save()
            print("modified "+ str(user))
            modified += 1
        else:
            user = User(number=number, name=line[1], taluka=line[2], village=line[3], allowed='y', indirect_bcasts_allowed=False)
            user.save()
            print("added "+ str(user))
            added += 1
            
    print(str(added)+" users added; "+str(modified)+" users modified")
    
'''
****************************************************************************
******************* MAIN ***************************************************
****************************************************************************
'''
def main():
    line = Line.objects.get(pk=LINEID)
    if len(sys.argv) < 3:
            print("report args: calleesfname <startdate> <enddate>")
            sys.exit()
        
    inbound = settings.INBOUND_LOG_ROOT + str(LINEID) + '.log'
    out_num = line.outbound_number or line.number
    outbound = settings.OUTBOUND_LOG_ROOT + out_num + '.log'
        
    if '--weeklyreport' in sys.argv:
        lineid = sys.argv[2]
        line = Line.objects.get(pk=int(lineid))
        out_num = line.outbound_number or line.number
    
        now = datetime.now()
        today = datetime(year=now.year, month=now.month, day=now.day)
        start = today-timedelta(days=6)
        
        monitoring_results(out_num, date_start=start)
    
    elif '--monthlyreport' in sys.argv:
        lineid = sys.argv[2]
        line = Line.objects.get(pk=int(lineid))
        calleesfname = sys.argv[3]
        out_num = line.outbound_number or line.number
        outbound = settings.OUTBOUND_LOG_ROOT + out_num + '.log'
    
        now = datetime.now()
        # assume we want the report for the previous month
        year = now.year
        month = now.month-1
        
        if now.month == 0:
            year -= 1
            month = 12
        
        start = datetime(year=year, month=month, day=1)
        
        callees_info = get_callees_info(calleesfname)
        
        results_by_callee(out_num, callees_info, date_start=start)
    elif '--report' in sys.argv:
        lineid = sys.argv[2]
        line = Line.objects.get(pk=int(lineid))
        out_num = line.outbound_number or line.number
        
        start=None  
        if len(sys.argv) > 3:
            start = datetime.strptime(sys.argv[3], "%m-%d-%Y")
        end = None    
        if len(sys.argv) > 4:
            end = datetime.strptime(sys.argv[4], "%m-%d-%Y")
        
        monitoring_results(out_num, date_start=start, date_end=end)
    elif '--add_users' in sys.argv:
        calleesfname = sys.argv[2]
        add_users(calleesfname)
    elif '--monitoring_survey' in sys.argv:
        lineid = sys.argv[2]
        line = Line.objects.get(pk=str(lineid))
        qnames = sys.argv[3]
        qnames = qnames.split(',')
        qnames = [name.strip() for name in qnames]
        
        for qname in qnames:
            monitoring_template(line,qname) 
    elif '--monthly_calls' in sys.argv:
        start = datetime.strptime(sys.argv[3], "%m-%d-%Y")
        end = None    
        if len(sys.argv) > 4:
            end = datetime.strptime(sys.argv[4], "%m-%d-%Y")
        monthly_calls(inbound, line.number, start, end)
    elif '--standard_template' in sys.argv:
        lineid = sys.argv[2]
        line = Line.objects.get(pk=int(lineid))
        contenttype = sys.argv[3]
        standard_template(line, contenttype)
    elif '--features_report' in sys.argv or '--features_report_weekly' in sys.argv:
        lineid = sys.argv[2]
        line = Line.objects.get(pk=int(lineid))
        inbound = settings.INBOUND_LOG_ROOT + lineid + '.log'
        
        start=end=None
        if '--features_report_weekly' in sys.argv:
            now = datetime.now()
            today = datetime(year=now.year, month=now.month, day=now.day)
            start = today-timedelta(days=6)
        else:
            if len(sys.argv) > 3:
                start = datetime.strptime(sys.argv[3], "%m-%d-%Y")    
            if len(sys.argv) > 4:
                end = datetime.strptime(sys.argv[4], "%m-%d-%Y")
            
        features=['activityofweek', 'qna', 'suggesexp', 'okyourreplies', 'okrecord', 'okplay']
        features_report(line, features, inbound, date_start=start, date_end=end)
    elif '--messages_report' in sys.argv or '--messages_report_weekly' in sys.argv:
        lineid = sys.argv[2]
        line = Line.objects.get(pk=int(lineid))
        
        start=end=None
        if '--messages_report_weekly' in sys.argv:
            now = datetime.now()
            today = datetime(year=now.year, month=now.month, day=now.day)
            start = today-timedelta(days=6)
        else:
            if len(sys.argv) > 3:
                start = datetime.strptime(sys.argv[3], "%m-%d-%Y")    
            if len(sys.argv) > 4:
                end = datetime.strptime(sys.argv[4], "%m-%d-%Y")
                
        messages(line, date_start=start, date_end=end, outputdir=OUTPUT_FILE_DIR)
    elif '--add_tags' in sys.argv:
        forumids = sys.argv[2]
        forumids = forumids.split(',')
        forumids = [id.strip() for id in forumids]
        forums = Forum.objects.filter(pk__in=forumids)
        
        tags = sys.argv[3]
        tags = tags.split(',')
        tags = [t.strip() for t in tags]
        
        for tag in tags:
            code = tag[:tag.find('-')+1]
            tags = Tag.objects.filter(tag__startswith=code, forum__in=forums)
            if not bool(tags):
                tag1 = Tag.objects.create(tag=tag, type='agri-crop')
                tag2 = Tag.objects.create(tag=tag, type='agri-topic')
            else:
                tag1 = tags.filter(type='agri-crop')[0]
                tag2 = tags.filter(type='agri-topic')[0]
                # update the name
                tags.update(tag=tag)
            
            for f in forums:
                fts = Forum_tag.objects.filter(forum=f, tag=tag1)
                if not bool(fts):
                    Forum_tag.objects.create(forum=f, tag=tag1)
                    Forum_tag.objects.create(forum=f, tag=tag2)
                    print("adding "+str(tag1)+" to "+str(f))
                
    elif '--main' in sys.argv:
        f1 = Forum.objects.get(pk=360)
        f2 = Forum.objects.get(pk=361)
        tags = '1-Training Feedback,1.1-Aww feedback  hygiene training,1.2-Supervisor feedback hygiene training,1.3-Aww feedback  Nutrition training,1.4-Supervisor feedback Nutrition training,2-Songs & episodes,2.1-Hyg song,2.1(a)-Jaag ,2.1 (b)-Safai main bhi hai masti,2.1 (c)-Dholo haath,2.1 (d)-Dhanyawad Shukriya Thank you,2.2-Hyg Episode,2.2 (a)-Saaf Sundari,2.2 (b)-Kitanu Raja,2.3 (c)-Shikki Shikki,2.3-Nut Song,2.4-Nut Episode,3-Print material,3.1-Hand washing cards,3.2-Hygiene Cut outs,3.3-Hyg story book,3.4-Hyg kit feedback ,3.5-Hyg parent material,3.6-Hyg Flash cards,3.7-Food flash cards,3.8-Nut Board game,3.9-Nut Story books ,3.1-Nut Parent material,3.11-Thali,3.12-Nut kit feedback ,4-Questions & Suggestions,4.1-Supervisor- Question & Suggestion,4.2-Anganwadi worker- Question & Suggestion,5-Interaction,5.1- Song/ children,5.2-Material/ children,5.3-Ques & Ans/ children,5.4-Parent talking,6-Child Speaking,7-Enrollment,8-Blank calls,9-Test calls,10-Hyg general,11-Nut general'
        tags = tags.split(',')
        for tag in tags:
            tag1 = Tag.objects.filter(tag=tag)
            if not bool(tag1):
                tag1 = Tag.objects.create(tag=tag, type='agri-crop')
                tag2 = Tag.objects.create(tag=tag, type='agri-topic')
                
                Forum_tag.objects.create(forum=f1, tag=tag1)
                Forum_tag.objects.create(forum=f1, tag=tag2)
                print("adding "+str(tag1)+" to "+str(f1))
                Forum_tag.objects.create(forum=f2, tag=tag1)
                Forum_tag.objects.create(forum=f2, tag=tag2)
                print("adding "+str(tag1)+" to "+str(f2))
                
#        old_names = 'PMQ_H&H_230213,CMQ_H&H_20313,PMQ_H&H_90313,CMQ_H&H_160313,CMQ_H&H_230313,PMQ_H&H_300313,CMQ_H&H_60413,PMQ_H&H_130413,CMQ_H&H_200413,CMQ_H&H_270413,PMQ_H&H_110513'
#        old_names = old_names.split(',')
#        new_names = 'PMQ_H&H_20313,CMQ_H&H_90313,PMQ_H&H_160313,CMQ_H&H_230313,CMQ_H&H_300313,PMQ_H&H_60413,CMQ_H&H_130413,PMQ_H&H_200413,CMQ_H&H_270413,CMQ_H&H_40513,CMQ_H&H_110513'
#        new_names = new_names.split(',')
#        
#        for i in range(len(old_names)):
#            s = Survey.objects.filter(number='7967776066', name=old_names[i])
#            if bool(s):
#                s = s[0]
#                new_name = new_names[i]
#                print('changing name of '+str(s)+' to '+new_name)
#                s.name = new_name
#                s.save()
#            else:
#                print(old_names[i]+' survey not found')
            
    else:
        print("Command not found.")
        
main()