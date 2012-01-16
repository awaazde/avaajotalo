import os, sys, csv, shutil
from datetime import datetime, timedelta
from django.conf import settings
from otalo.surveys.models import Subject, Survey, Prompt, Option, Param, Call, Input
from otalo.AO.models import Line
import otalo_utils

'''
****************************************************************************
******************* CONSTANTS **********************************************
****************************************************************************
'''
OUTPUT_FILE_DIR='/home/wednesdays/reports/'
PREFIX='freetdm/grp1/a/0'
SUFFIX=''
SOUND_EXT = ".wav"
BARGEIN_KEY='9'
SUBDIR = 'weds/'

'''
****************************************************************************
******************* SURVEY GENERATION ****************************************
****************************************************************************
'''
def create_survey(number, inbound=False, template=False):
    s = Survey.objects.filter(name='Wednesdays', number=number, inbound=inbound, template=template)
    if bool(s):
        s = s[0]
        s.delete()
    s = Survey(name='Wednesdays', number=number, dialstring_prefix=PREFIX, dialstring_suffix=SUFFIX, complete_after=0, inbound=inbound, template=template)
    s.save()    
    
    order = 1
    welcome = Prompt(file=SUBDIR+"welcome"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
    welcome.save()
    welcome_opt = Option(number="1", action=Option.GOTO, prompt=welcome)
    welcome_opt.save()
    welcome_opt2 = Option(number="2", action=Option.GOTO, prompt=welcome)
    welcome_opt2.save()
    welcome_opt3 = Option(number="3", action=Option.GOTO, prompt=welcome)
    welcome_opt3.save()
    order+=1
    
    rsvp = Prompt(file=SUBDIR+"rsvp"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
    rsvp.save()
    rsvp_opt1 = Option(number="1", action=Option.INPUT, prompt=rsvp)
    rsvp_opt1.save()
    rsvp_opt2 = Option(number="2", action=Option.INPUT, prompt=rsvp)
    rsvp_opt2.save()
    rsvp_opt3 = Option(number="3", action=Option.INPUT, prompt=rsvp)
    rsvp_opt3.save()
    rsvp_opt4 = Option(number="4", action=Option.INPUT, prompt=rsvp)
    rsvp_opt4.save()
    rsvp_opt5 = Option(number="5", action=Option.INPUT, prompt=rsvp)
    rsvp_opt5.save()
    rsvp_opt6 = Option(number="6", action=Option.INPUT, prompt=rsvp)
    rsvp_opt6.save()
    rsvp_opt7 = Option(number="7", action=Option.INPUT, prompt=rsvp)
    rsvp_opt7.save()
    rsvp_opt8 = Option(number="8", action=Option.INPUT, prompt=rsvp)
    rsvp_opt8.save()
    rsvp_opt9 = Option(number="9", action=Option.INPUT, prompt=rsvp)
    rsvp_opt9.save()
    order+= 1
    
    param = Param(option=welcome_opt, name=Param.IDX, value=rsvp.order)
    param.save()
    
    # go back to welcome prompt
    rsvp_thankyou = Prompt(file=SUBDIR+"rsvp_thankyou"+SOUND_EXT, order=order, survey=s)
    rsvp_thankyou.save()
    rsvp_thankyou_opt = Option(number="", action=Option.GOTO, prompt=rsvp_thankyou)
    rsvp_thankyou_opt.save()
    param = Param(option=rsvp_thankyou_opt, name=Param.IDX, value=welcome.order)
    param.save()
    order+=1
    
    # keep a gap for the TOW, but have the welcome prompt jump to the gap
    param = Param(option=welcome_opt2, name=Param.IDX, value=order)
    param.save()
    order +=1
    
    # go back to welcome prompt
    tow_post = Prompt(file=SUBDIR+"blank"+SOUND_EXT, order=order, survey=s, delay=0)
    tow_post.save()
    tow_post_opt = Option(number="", action=Option.GOTO, prompt=tow_post)
    tow_post_opt.save()
    param = Param(option=tow_post_opt, name=Param.IDX, value=welcome.order)
    param.save()
    order+=1
    
    directions = Prompt(file=SUBDIR+"directions"+SOUND_EXT, order=order, bargein=True, survey=s)
    directions.save()
    directions_opt = Option(number=BARGEIN_KEY, action=Option.GOTO, prompt=directions)
    directions_opt.save()
    param = Param(option=directions_opt, name=Param.IDX, value=welcome.order)
    param.save()
    directions_opt2 = Option(number="", action=Option.GOTO, prompt=directions)
    directions_opt2.save()
    param = Param(option=directions_opt2, name=Param.IDX, value=welcome.order)
    param.save()
    order += 1
    
    param = Param(option=welcome_opt3, name=Param.IDX, value=directions.order)
    param.save()
        
    return s

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
******************* Reporting **********************************************
****************************************************************************
'''
    
def survey_results(survey_number, date_start=False, date_end=False):
    # get calls
    calls = Call.objects.filter(survey__number=survey_number, complete=True)
    
    if date_start:
        calls = calls.filter(date__gte=date_start)
        
    if date_end:
        calls = calls.filter(date__lt=date_end)
    
    header = ['CallId', 'CallerNum', 'time', 'rsvp count']
    results = [header]
    for call in calls:
        inputs = Input.objects.filter(call=call)
        result = [str(call.id), call.subject.number, time_str(call.date)]
        for input in inputs:
            result.append(input.input)
                    
        results.append(result)
    
    if date_start:
        outfilename='weds_rsvps_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]+'.csv'
    else:
        outfilename='weds_rsvps'+survey_number+'.csv'
        
    outfilename = OUTPUT_FILE_DIR+outfilename
    output = csv.writer(open(outfilename, 'wb'))
    output.writerows(results)
    
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
    if len(sys.argv) < 2:
        print("arg1: lineid")
        sys.exit()
    else:
        lineid = sys.argv[1]
        line = Line.objects.get(pk=lineid)
        num = line.outbound_number or line.number
        
    create_survey(num,template=True)
    create_survey(num,inbound=True)
   
main()