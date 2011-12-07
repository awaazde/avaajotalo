import os, sys, csv
from openpyxl.reader.excel import load_workbook
from datetime import datetime, timedelta
from django.db.models import Q, Max
from django.conf import settings
from otalo.surveys.models import Subject, Survey, Prompt, Option, Param, Call
import otalo_utils

'''
****************************************************************************
******************* CONSTANTS **********************************************
****************************************************************************
'''
OUTPUT_FILE_DIR = ''
PREFIX='freetdm/grp3/a/'
SUFFIX=''
NUMBER='796604400'
SUBDIR = 'akrsp/'
SOUND_EXT = ".wav"
BARGEIN_KEY='1'
CROP_NAMES = ['bhinda', 'karela', 'kela', 'keri', 'parwal', 'ringal', 'tameta']
MONTHS=['january','february','march','april','may','june','july','august','september','october','november','december']
DAYS_OF_WEEK=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
MAX_DIGITS=5
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
    
    s = Survey(name='AKRSP_SURVEY_' + date_str(date), dialstring_prefix=PREFIX, dialstring_suffix=SUFFIX, complete_after=0, number=NUMBER, inbound=True)
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
    
    for dt in range(1,NUM_DAYS+1):
        date += timedelta(days=dt)
        day_o_month = str(date.day)
        month = MONTHS[date.month-1]
        day_o_week = DAYS_OF_WEEK[date.weekday()]
        
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
        param = Param(option=day_prompt_optR, name=Param.IDX, value=collection_for_date.order)
        param.save()
        order+= 1
        
        digit_prompts=[day_prompt]
        for dig in range(MAX_DIGITS-1,0,-1):
            digit = Prompt(file=SUBDIR+"blank"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
            digit.save()
            digit_prompts.append(digit)
            # if user is done entering, move on to confirmation
            digit_opt = Option(number="", action=Option.INPUT, prompt=digit)
            digit_opt.save()
            param = Param(option=digit_opt, name=Param.IDX, value=order+dig)
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
        enter_pre_opt = Option(number="", action=Option.GOTO, prompt=enter_pre)
        enter_pre_opt.save()
        order += 1
    
        '''
        Note for reporting: Will will have to get the number starting from the latest input to the day_prompt, and *only*
        get input values with increasing IDs (to avoid picking up a digit from a longer overwritten entry)
        '''
        
        for dig in range(MAX_DIGITS-1):
            confirm_digit = Prompt(file=SUBDIR+"nums/", order=order, bargein=False, survey=s, delay=0, dependson=digit_prompts[dig])
            confirm_digit.save()
            confirm_digit_opt = Option(number="", action=Option.NEXT, prompt=confirm_digit)
            confirm_digit_opt.save()
            order += 1
        
        enter_post = Prompt(file=SUBDIR+"enter_post"+SOUND_EXT, order=order, bargein=False, survey=s, delay=0)
        enter_post.save()
        enter_post_opt = Option(number="1", action=Option.GOTO, prompt=enter_post)
        enter_post_opt.save()
        param = Param(option=enter_post_opt, name=Param.IDX, value=order+2)
        param.save()
        enter_post_opt2 = Option(number="2", action=Option.GOTO, prompt=enter_post)
        enter_post_opt2.save()
        param2 = Param(option=enter_post_opt2, name=Param.IDX, value=day_prompt.order)
        param2.save()
        order += 1
        
        dontknow = Prompt(file=SUBDIR+"if_star"+SOUND_EXT, order=order, bargein=False, survey=s, delay=0)
        dontknow.save()
        dontknow_opt = Option(number="", action=Option.NEXT, prompt=dontknow)
        dontknow_opt.save()        
        dontknow_opt2 = Option(number=BARGEIN_KEY, action=Option.NEXT, prompt=dontknow)
        dontknow_opt2.save()    
        order += 1
        
        param = Param(option=day_prompt_opt10, name=Param.IDX, value=order)
        param.save()
    
    thankyou = Prompt(file=SUBDIR+"thankyou_survey"+SOUND_EXT, order=order, bargein=False, survey=s, delay=0)
    thankyou.save()
    thankyou_opt = Option(number="", action=Option.NEXT, prompt=thankyou)
    thankyou_opt.save()
    order += 1
    
    return s

'''
****************************************************************************
******************* REPORTING **********************************************
****************************************************************************
'''


'''
****************************************************************************
******************* UTILS **************************************************
****************************************************************************
'''

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
    if len(sys.argv) > 1:
        startdate = datetime.strptime(sys.argv[1], "%m-%d-%Y")
    else:
       now = datetime.now()
       startdate = datetime(year=now.year, month=now.month, day=now.day)
   
    survey(startdate)

main()