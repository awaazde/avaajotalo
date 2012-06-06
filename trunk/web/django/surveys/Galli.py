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
from django.conf import settings
from otalo.AO.models import Line
from otalo.surveys.models import Survey, Subject, Call, Prompt, Option, Param

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
    
    name = contenttype[:3].upper()
    s = Survey.objects.filter(name=name, number=number, template=True)
    if bool(s):
        s = s[0]
        s.delete()
        print('deleting survey')
    s = Survey(name=name, number=number, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0, template=True)
    s.save()
    print('creating new survey '+str(s))
    
    # welcome
    welcome = Prompt(file=language+"/welcome_"+contenttype[:3].upper()+SOUND_EXT, order=1, bargein=True, survey=s)
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
    thanks = Prompt(file=language+"/thankyou_"+contenttype[:3].upper()+SOUND_EXT, order=3, bargein=True, survey=s)
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
    
    welcome = Prompt(file=language+"/MFQw"+SOUND_EXT, order=1, bargein=True, survey=s)
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
    question_opt3 = Option(number="4", action=Option.INPUT, prompt=question)
    question_opt3.save()
        
    thanks = Prompt(file=language+"/MFQe"+SOUND_EXT, order=3, bargein=True, survey=s)
    thanks.save()
    thanks_opt1 = Option(number="", action=Option.NEXT, prompt=thanks)
    thanks_opt1.save()
    
    return s

'''
****************************************************************************
******************* REPORTING **********************************************
****************************************************************************
'''
        
def monitoring_results(number, filename, callees_info, phone_num_filter=False, date_start=False, date_end=False):
    all_calls = []
    open_calls = {}
    questions = set()
    
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
                    # close out call                
                    open_call = open_calls[phone_num]    
                    start = open_call['start']
                    dur = current_date - start
                    call = Call.objects.filter(subject__number=phone_num, date__gte=start-timedelta(seconds=40), date__lte=start+timedelta(seconds=40), complete=True)
                    if bool(call):
                        if call.count()>1:
                            print("more than one call found: " + str(call))
                        call = call[0]
                        groupid = get_groupid(phone_num, callees_info)
                        result = [call.subject.number, call.subject.name or '', groupid, time_str(call.date), str(dur.seconds)]
        
                        inputs = Input.objects.select_related(depth=1).filter(call=call).order_by('id')
                        
                        for input in inputs:
                            result.append(input.input)
                            prompt = input.prompt
                            questions.add(prompt.file[prompt.file.rfind('/')+1:prompt.file.find(SOUND_EXT)])                        
                        all_calls.append(result)
                    else:
                        print("no call found: num=" +phone_num+ ";sessid ="+ otalo_utils.get_sessid(line)+ ";start="+start.strftime('%m-%d-%y %H:%M:%S'))
                    del open_calls[phone_num]
                    
                # add new call
                #print("adding new call: " + phone_num)
                open_calls[phone_num] = {'start':current_date}
                
            elif line.find("End call") != -1 or line.find("Abort call") != -1:
                if phone_num in open_calls:
                    open_call = open_calls[phone_num]    
                    start = open_call['start']
                    dur = current_date - start
                    call = Call.objects.filter(subject__number=phone_num, date__gte=start-timedelta(seconds=40), date__lte=start+timedelta(seconds=40), complete=True)
                    if bool(call):
                        if call.count()>1:
                            print("more than one call found: " + str(call))
                        call = call[0]
                        groupid = get_groupid(phone_num, callees_info)
                        result = [call.subject.number, call.subject.name or '', groupid, time_str(call.date), str(dur.seconds)]
        
                        inputs = Input.objects.select_related(depth=1).filter(call=call).order_by('id')
                        
                        for input in inputs:
                            result.append(input.input)
                            prompt = input.prompt
                            questions.add(prompt.file[prompt.file.rfind('/')+1:prompt.file.find(SOUND_EXT)])                       
                        all_calls.append(result)
                    else:
                        print("no call found: num=" +phone_num+ ";sessid ="+ otalo_utils.get_sessid(line)+ ";start="+start.strftime('%m-%d-%y %H:%M:%S'))
                    del open_calls[phone_num]
                    
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
    
    header = ['number','name','groupid','start','duration (s)']
    question = 'Response'
    if len(questions) == 1:
        question = list(questions)[0]
    header.append(question)
    outputfilename='survey_results_'+number
    if date_start:
        outputfilename+='_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]
    outputfilename = OUTPUT_FILE_DIR+outputfilename+'.csv'
    output = csv.writer(open(outputfilename, 'wb'))
    output.writerow(header)            
    output.writerows(all_calls)

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
            info[num] = line[1:]
            
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

def get_groupid(number, callees_info):
    groupid = ''
    if number in callees_info:
        groupid = callees_info[number][2].strip()
    return groupid
    

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
        
    if '--weeklyreports' in sys.argv:
        now = datetime.now()
        today = datetime(year=now.year, month=now.month, day=now.day)
        start = today-timedelta(days=6)
        
        callees_info = {}
        #callees_info = get_callees_info(callees_fname)
        
        monitoring_results(out_num, outbound, callees_info, date_start=start)
    elif '--report' in sys.argv:
        start=None  
        callees_fname = sys.argv[2]
        
        if len(sys.argv) > 3:
            start = datetime.strptime(sys.argv[3], "%m-%d-%Y")
        end = None    
        if len(sys.argv) > 4:
            end = datetime.strptime(sys.argv[4], "%m-%d-%Y")
        
        callees_info = {}
        #callees_info = get_callees_info(callees_fname)
        
        monitoring_results(out_num, outbound, callees_info, date_start=start, date_end=end)
    
        
main()

