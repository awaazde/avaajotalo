import os, sys, csv
from openpyxl.reader.excel import load_workbook
from datetime import datetime, timedelta
from django.db.models import Q, Max
from django.conf import settings
from otalo.surveys.models import Subject, Survey, Prompt, Option, Param, Call, Input
import otalo_utils

'''
****************************************************************************
******************* CONSTANTS **********************************************
****************************************************************************
'''
OUTPUT_FILE_DIR = '/home/akrsp/reports/'
PREFIX='freetdm/grp3/a/'
SUFFIX=''
NUMBER='7966044411'
SUBDIR = 'akrsp/'
SOUND_EXT = ".wav"
BARGEIN_KEY='1'
CROP_NAMES = ['bhinda', 'karela', 'kela', 'keri', 'parwal', 'ringal', 'tameta']
MONTHS=['january','february','march','april','may','june','july','august','september','october','november','december']
DAYS_OF_WEEK=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
MAX_DIGITS=4
NUM_DAYS=4

'''
****************************************************************************
******************* SURVEY GENERATION **************************************
****************************************************************************
'''

def survey(date):
    s = Survey.objects.filter(name='AKRSP_SURVEY_' + date_str(date))
    if bool(s):
        s[0].delete()
    
    s = Survey(name='AKRSP_SURVEY_' + date_str(date), dialstring_prefix=PREFIX, dialstring_suffix=SUFFIX, complete_after=0, number=NUMBER, inbound=True, callback=True)
    s.save()
    print('Survey created: '+str(s))
    
    order = 1
    welcome = Prompt(file=SUBDIR+"welcome_survey"+SOUND_EXT, order=order, bargein=True, survey=s, delay=0)
    welcome.save()
    welcome_opt = Option(number=BARGEIN_KEY, action=Option.NEXT, prompt=welcome)
    welcome_opt.save()
    welcome_opt2 = Option(number="", action=Option.NEXT, prompt=welcome)
    welcome_opt2.save()
    order += 1
    
    select_crop = Prompt(file=SUBDIR+"crop_options"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
    select_crop.save()
    number = 1
    for crop in CROP_NAMES:
        crop_opt = Option(number=str(number), action=Option.INPUT, prompt=select_crop)
        crop_opt.save()
        param = Param(option=crop_opt, name=Param.NAME, value=crop)
        param.save()
        number += 1
    order += 1
    
    confirm = Prompt(file=SUBDIR+"confirm"+SOUND_EXT, order=order, bargein=False, survey=s, delay=0)
    confirm.save()
    confirm_opt = Option(number="", action=Option.NEXT, prompt=confirm)
    confirm_opt.save()
    order += 1
    
    confirm_crop = Prompt(file=SUBDIR+"crops/", order=order, bargein=False, survey=s, delay=0, dependson=select_crop)
    confirm_crop.save()
    confirm_crop_opt = Option(number="", action=Option.NEXT, prompt=confirm_crop)
    confirm_crop_opt.save()
    order += 1
    
    collection = Prompt(file=SUBDIR+"collection"+SOUND_EXT, order=order, bargein=True, survey=s, delay=0)
    collection.save()
    collection_opt = Option(number=BARGEIN_KEY, action=Option.NEXT, prompt=collection)
    collection_opt.save()
    collection_opt2 = Option(number="", action=Option.NEXT, prompt=collection)
    collection_opt2.save()
    order += 1
    
    for i in range(1,NUM_DAYS+1):
        dt = date + timedelta(days=i)
        day_o_month = str(dt.day)
        month = MONTHS[dt.month-1]
        day_o_week = DAYS_OF_WEEK[dt.weekday()]
        
        confirm_crop2 = Prompt(file=SUBDIR+"crops/", order=order, bargein=False, survey=s, delay=0, dependson=select_crop)
        confirm_crop2.save()
        confirm_crop2_opt = Option(number="", action=Option.NEXT, prompt=confirm_crop2)
        confirm_crop2_opt.save()
        order += 1
        
        collection_for_date = Prompt(file=SUBDIR+"collection_for_date"+SOUND_EXT, order=order, bargein=True, survey=s, delay=0)
        collection_for_date.save()
        collection_for_date_opt = Option(number=BARGEIN_KEY, action=Option.NEXT, prompt=collection_for_date)
        collection_for_date_opt.save()
        collection_for_date_opt2 = Option(number="", action=Option.NEXT, prompt=collection_for_date)
        collection_for_date_opt2.save()
        order += 1
        
        date_prompt = Prompt(file=SUBDIR+"nums/"+day_o_month+SOUND_EXT, order=order, bargein=False, survey=s, delay=0)
        date_prompt.save()
        date_prompt_opt = Option(number="", action=Option.NEXT, prompt=date_prompt)
        date_prompt_opt.save()
        order += 1
        
        month_prompt = Prompt(file=SUBDIR+"months/"+month+SOUND_EXT, order=order, bargein=False, survey=s, delay=0)
        month_prompt.save()
        month_prompt_opt = Option(number="", action=Option.NEXT, prompt=month_prompt)
        month_prompt_opt.save()
        order += 1
        
        # Have to capture digits seperately in this case because there are no digit prompts. But using input length works!
        day_prompt = Prompt(file=SUBDIR+"days/"+day_o_week+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
        day_prompt.save()
        day_prompt_opt0 = Option(number="0", action=Option.INPUT, prompt=day_prompt)
        day_prompt_opt0.save()
        day_prompt_opt1 = Option(number="1", action=Option.INPUT, prompt=day_prompt)
        day_prompt_opt1.save()
        day_prompt_opt2 = Option(number="2", action=Option.INPUT, prompt=day_prompt)
        day_prompt_opt2.save()
        day_prompt_opt3 = Option(number="3", action=Option.INPUT, prompt=day_prompt)
        day_prompt_opt3.save()
        day_prompt_opt4 = Option(number="4", action=Option.INPUT, prompt=day_prompt)
        day_prompt_opt4.save()
        day_prompt_opt5 = Option(number="5", action=Option.INPUT, prompt=day_prompt)
        day_prompt_opt5.save()
        day_prompt_opt6 = Option(number="6", action=Option.INPUT, prompt=day_prompt)
        day_prompt_opt6.save()
        day_prompt_opt7 = Option(number="7", action=Option.INPUT, prompt=day_prompt)
        day_prompt_opt7.save()
        day_prompt_opt8 = Option(number="8", action=Option.INPUT, prompt=day_prompt)
        day_prompt_opt8.save()
        day_prompt_opt9 = Option(number="9", action=Option.INPUT, prompt=day_prompt)
        day_prompt_opt9.save()
        day_prompt_opt10 = Option(number="*", action=Option.INPUT, prompt=day_prompt)
        day_prompt_opt10.save()
        day_prompt_optR = Option(number="", action=Option.GOTO, prompt=day_prompt)
        day_prompt_optR.save()
        param = Param(option=day_prompt_optR, name=Param.IDX, value=confirm_crop2.order)
        param.save()
        order+= 1
        
        digit_prompts=[day_prompt]
        for dig in range(MAX_DIGITS-1):
            digit = Prompt(file=SUBDIR+"blank"+SOUND_EXT, order=order, bargein=True, survey=s, delay=2000, name='d'+str(dig+2))
            digit.save()
            digit_prompts.append(digit)
            # take blank as input to zero out all possible digits
            digit_opt = Option(number="", action=Option.INPUT, prompt=digit)
            digit_opt.save()
            param = Param(option=digit_opt, name=Param.NAME, value="blank")
            param.save()
            digit_opt0 = Option(number="0", action=Option.INPUT, prompt=digit)
            digit_opt0.save()
            digit_opt1 = Option(number="1", action=Option.INPUT, prompt=digit)
            digit_opt1.save()
            digit_opt2 = Option(number="2", action=Option.INPUT, prompt=digit)
            digit_opt2.save()
            digit_opt3 = Option(number="3", action=Option.INPUT, prompt=digit)
            digit_opt3.save()
            digit_opt4 = Option(number="4", action=Option.INPUT, prompt=digit)
            digit_opt4.save()
            digit_opt5 = Option(number="5", action=Option.INPUT, prompt=digit)
            digit_opt5.save()
            digit_opt6 = Option(number="6", action=Option.INPUT, prompt=digit)
            digit_opt6.save()
            digit_opt7 = Option(number="7", action=Option.INPUT, prompt=digit)
            digit_opt7.save()
            digit_opt8 = Option(number="8", action=Option.INPUT, prompt=digit)
            digit_opt8.save()
            digit_opt9 = Option(number="9", action=Option.INPUT, prompt=digit)
            digit_opt9.save()
            order+= 1
        
        enter_pre = Prompt(file=SUBDIR+"enter_pre"+SOUND_EXT, order=order, bargein=False, survey=s, delay=0)
        enter_pre.save()
        enter_pre_opt = Option(number="", action=Option.NEXT, prompt=enter_pre)
        enter_pre_opt.save()
        order += 1
    
        '''
        Note for reporting: Will will have to get the number starting from the latest input to the day_prompt, and *only*
        get input values with increasing IDs (to avoid picking up a digit from a longer overwritten entry)
        '''
        
        # playback/confirm
        for dig in range(MAX_DIGITS):
            confirm_digit = Prompt(file=SUBDIR+"nums/", order=order, bargein=False, survey=s, delay=0, dependson=digit_prompts[dig])
            confirm_digit.save()
            confirm_digit_opt = Option(number="", action=Option.NEXT, prompt=confirm_digit)
            confirm_digit_opt.save()
            order += 1
        
        enter_post = Prompt(file=SUBDIR+"enter_post"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
        enter_post.save()
        enter_post_opt = Option(number="1", action=Option.GOTO, prompt=enter_post)
        enter_post_opt.save()
        param = Param(option=enter_post_opt, name=Param.IDX, value=order+3)
        param.save()
        enter_post_opt2 = Option(number="2", action=Option.GOTO, prompt=enter_post)
        enter_post_opt2.save()
        param2 = Param(option=enter_post_opt2, name=Param.IDX, value=confirm_crop2.order)
        param2.save()
        order += 1
        
        dontknow = Prompt(file=SUBDIR+"if_star"+SOUND_EXT, order=order, bargein=False, survey=s, delay=0)
        dontknow.save()
        dontknow_opt = Option(number="", action=Option.NEXT, prompt=dontknow)
        dontknow_opt.save()        
        dontknow_opt2 = Option(number=BARGEIN_KEY, action=Option.NEXT, prompt=dontknow)
        dontknow_opt2.save()    
        order += 1
        
        param = Param(option=day_prompt_opt10, name=Param.IDX, value=dontknow.order)
        param.save()
        
        confirm_dontknow = Prompt(file=SUBDIR+"enter_post"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
        confirm_dontknow.save()
        confirm_dontknow_opt = Option(number="1", action=Option.NEXT, prompt=confirm_dontknow)
        confirm_dontknow_opt.save()
        confirm_dontknow_opt2 = Option(number="2", action=Option.GOTO, prompt=confirm_dontknow)
        confirm_dontknow_opt2.save()
        param2 = Param(option=confirm_dontknow_opt2, name=Param.IDX, value=confirm_crop2.order)
        param2.save()
        order += 1
    
    thankyou = Prompt(file=SUBDIR+"thankyou_survey"+SOUND_EXT, order=order, bargein=False, survey=s, delay=3000)
    thankyou.save()
    thankyou_opt = Option(number="", action=Option.GOTO, prompt=thankyou)
    thankyou_opt.save()
    param = Param(option=thankyou_opt, name=Param.IDX, value=select_crop.order)
    param.save()
    order += 1
    
    return s

def data_coll_reminders():
    reminders = Survey.objects.filter(name__contains='COLLECTION_REM', number=NUMBER, template=True)
    if bool(reminders):
        for s in reminders:
            s.delete()
    
    s = Survey(name='COLLECTION_REM_DAY_PRIOR', dialstring_prefix=PREFIX, dialstring_suffix=SUFFIX, complete_after=0, number=NUMBER, template=True)
    s.save()
    print('Reminder template created: '+str(s))
    
    message = Prompt(file=SUBDIR+"collection_reminder_day_before"+SOUND_EXT, order=1, bargein=True, survey=s, delay=0)
    message.save()
    message_opt = Option(number="", action=Option.NEXT, prompt=message)
    message_opt.save()
    
    s = Survey(name='COLLECTION_REM_SAME_DAY', dialstring_prefix=PREFIX, dialstring_suffix=SUFFIX, complete_after=0, number=NUMBER, template=True)
    s.save()
    print('Reminder template created: '+str(s))
    
    message = Prompt(file=SUBDIR+"collection_reminder_same_day"+SOUND_EXT, order=1, bargein=True, survey=s, delay=0)
    message.save()
    message_opt = Option(number="", action=Option.NEXT, prompt=message)
    message_opt.save()

def blank_template(num, prefix, suffix):
    s = Survey.objects.filter(name__contains='BLANK', number=num, template=True)
    if not bool(s):
        s = Survey(name='BLANK', template=True, number=num, dialstring_prefix=prefix, dialstring_suffix=suffix, complete_after=0)
        s.save()
        print('Blank template created: '+str(s))
        
        blank = Prompt(file=SUBDIR+'blank.wav', order=1, bargein=False, survey=s, delay=0)
        blank.save()
        blank_opt = Option(number="", action=Option.NEXT, prompt=blank)
        blank_opt.save()
        
        return s
'''
****************************************************************************
******************* REPORTING **********************************************
****************************************************************************
'''
def collection_report(caller_info_file, date_start=False, date_end=False):
    caller_info = load_caller_info(caller_info_file)
    all_calls = []
    # get calls
    calls = Call.objects.select_related().filter(survey__number=NUMBER, complete=True)
    
    if date_start:
        calls = calls.filter(date__gte=date_start)
        
    if date_end:
        calls = calls.filter(date__lt=date_end)
    
    # write out the data
    header = ['number','name','village','time','crop','d1','d2','d3','d4']
    if date_start:
        outfilename='collection_report_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]+'.csv'
    else:
        outfilename='collection_report.csv'
    outfilename = OUTPUT_FILE_DIR+outfilename
    output = csv.writer(open(outfilename, 'wb'))
    output.writerow(header)
           
    for call in calls:
        subj = call.subject
        num = subj.number
        
        inputs = Input.objects.select_related(depth=1).filter(call=call).order_by('id')
        
        crops = {}
        crop = None
        entry = None
        for input in inputs:
            if 'crop_options' in input.prompt.file:
                crop = {}
                crops[input.input] = crop
            elif 'days' in input.prompt.file:
                # pack up old entry
                if entry:
                    crop[str(day)] = entry
                    
                # new day entry
                day = input.prompt.order
                entry = str(input.input)
            elif 'blank' in input.prompt.file:
                if input.input != 'blank':
                    entry += str(input.input)
               
        results=[]
        for cropname,values in crops.items():
            village = ''
            if num in caller_info:
                village = caller_info[num]['village']
            cropwise_data = [num, subj.name, village, time_str(call.date), cropname]  
            sorted_items = sorted(values.items())
            for order,val in sorted_items:
                cropwise_data.append(val)
            results.append(cropwise_data)
        output.writerows(results)

'''
****************************************************************************
******************* UTILS **************************************************
****************************************************************************
'''

def load_caller_info(filename):
    all_info = {}
    
    f = csv.reader(open(filename, "rU"))
    
    for line in f:        
        num = get_number(line)
        caller_info = {}

        caller_info['village'] = get_village(line)
        
        all_info[num] = caller_info
    
    return all_info
        
def get_number(line):
    # get last 10 digits only
    num = line[0][-10:]
    return num

def get_name(line):
    return line[1].strip()

def get_village(line):
    return line[2].strip()

def date_str(date):
    #return date.strftime('%Y-%m-%d')
    return date.strftime('%b-%d-%y')

def time_str(date):
    #return date.strftime('%Y-%m-%d')
    return date.strftime('%m-%d-%y %H:%M')


'''
****************************************************************************
******************* MAIN ***************************************************
****************************************************************************
'''

def main():
    if '--report' in sys.argv:
        collection_report(sys.argv[2])
    else:
        if len(sys.argv) > 1:
            startdate = datetime.strptime(sys.argv[1], "%m-%d-%Y")
        else:
            now = datetime.now()
            startdate = datetime(year=now.year, month=now.month, day=now.day)
       
        survey(startdate)
        #data_coll_reminders()
        #blank_template(NUMBER,PREFIX,SUFFIX)

main()