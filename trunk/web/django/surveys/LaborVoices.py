import os, sys, csv
from datetime import datetime, timedelta
from django.conf import settings
from otalo.surveys.models import Subject, Survey, Prompt, Option, Param, Call
import otalo_utils

'''
****************************************************************************
******************* CONSTANTS **********************************************
****************************************************************************
'''
PREFIX='freetdm/grp1/a/0'
SUFFIX=''
NUMBER='7961907779'
SUBDIR = 'lveng/'
SOUND_EXT = ".wav"
BARGEIN_KEY='9'

'''
****************************************************************************
******************* SURVEY GENERATION ****************************************
****************************************************************************
'''

def create_survey():
    s = Survey(name='LV_eng_DEMO_'+Survey.INBOUND_DESIGNATOR, number=NUMBER, dialstring_prefix=PREFIX, dialstring_suffix=SUFFIX, complete_after=0, callback=True)
    s.save()
        
    order = 1
    
    id = Prompt(file=SUBDIR+"id"+SOUND_EXT, order=order, bargein=True, survey=s, delay=5000, inputlen=4)
    id.save()
    for i in range(1000,2000):
        id_opt = Option(number=str(i), action=Option.INPUT, prompt=id)
        id_opt.save()
    order+=1
    
    welcome = Prompt(file=SUBDIR+"welcome"+SOUND_EXT, order=order, bargein=True, survey=s, delay=0)
    welcome.save()
    welcome_opt = Option(number="1", action=Option.NEXT, prompt=welcome)
    welcome_opt.save()
    welcome_opt2 = Option(number="2", action=Option.GOTO, prompt=welcome)
    welcome_opt2.save()
    welcome_opt3 = Option(number="3", action=Option.GOTO, prompt=welcome)
    welcome_opt3.save()
    order+=1
    
    survey = Prompt(file=SUBDIR+"survey"+SOUND_EXT, order=order, survey=s, delay=0)
    survey.save()
    survey_opt = Option(number="", action=Option.NEXT, prompt=survey)
    survey_opt.save()
    order+=1
    
    factory = Prompt(file=SUBDIR+"factory"+SOUND_EXT, order=order, survey=s)
    factory.save()
    record_opt = Option(number="", action=Option.RECORD, prompt=factory)
    record_opt.save()
    order+=1
    
    working_hours = Prompt(file=SUBDIR+"working_hours"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
    working_hours.save()
    working_hours_opt = Option(number="1", action=Option.INPUT, prompt=working_hours)
    working_hours_opt.save()
    working_hours_opt2 = Option(number="2", action=Option.INPUT, prompt=working_hours)
    working_hours_opt2.save()
    working_hours_opt3 = Option(number="3", action=Option.INPUT, prompt=working_hours)
    working_hours_opt3.save()
    working_hours_opt4 = Option(number="4", action=Option.INPUT, prompt=working_hours)
    working_hours_opt4.save()
    order+= 1
    
    overtime_wages = Prompt(file=SUBDIR+"overtime_wages"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
    overtime_wages.save()
    overtime_wages_opt = Option(number="1", action=Option.INPUT, prompt=overtime_wages)
    overtime_wages_opt.save()
    overtime_wages_opt2 = Option(number="2", action=Option.INPUT, prompt=overtime_wages)
    overtime_wages_opt2.save()
    overtime_wages_opt3 = Option(number="3", action=Option.INPUT, prompt=overtime_wages)
    overtime_wages_opt3.save()
    overtime_wages_opt4 = Option(number="4", action=Option.INPUT, prompt=overtime_wages)
    overtime_wages_opt4.save()
    order+= 1
    
    harassment = Prompt(file=SUBDIR+"harassment"+SOUND_EXT, order=order, survey=s)
    harassment.save()
    record_opt = Option(number="", action=Option.RECORD, prompt=harassment)
    record_opt.save()
    order+=1
    
    brand = Prompt(file=SUBDIR+"brand"+SOUND_EXT, order=order, survey=s)
    brand.save()
    record_opt = Option(number="", action=Option.RECORD, prompt=brand)
    record_opt.save()
    order+=1
    
    thankyou = Prompt(file=SUBDIR+"thank_you"+SOUND_EXT, order=order, bargein=True, survey=s, delay=0)
    thankyou.save()
    thankyou_opt = Option(number="", action=Option.GOTO, prompt=thankyou)
    thankyou_opt.save()
    order+=1
    
    disconnect_future = Prompt(file=SUBDIR+"disconnect_future"+SOUND_EXT, order=order, bargein=True, survey=s, delay=0)
    disconnect_future.save()
    disconnect_future_opt = Option(number="", action=Option.GOTO, prompt=disconnect_future)
    disconnect_future_opt.save()
    
    param = Param(option=welcome_opt2, name=Param.IDX, value=order)
    param.save()
    order+=1
    
    disconnect_remove = Prompt(file=SUBDIR+"disconnect_remove"+SOUND_EXT, order=order, bargein=True, survey=s, delay=0)
    disconnect_remove.save()
    disconnect_remove_opt = Option(number="", action=Option.GOTO, prompt=disconnect_remove)
    disconnect_remove_opt.save()
    
    param = Param(option=welcome_opt3, name=Param.IDX, value=order)
    param.save()
    order+=1
    
    param = Param(option=thankyou_opt, name=Param.IDX, value=order)
    param.save()
    
    param = Param(option=disconnect_future_opt, name=Param.IDX, value=order)
    param.save()
    
    param = Param(option=disconnect_remove_opt, name=Param.IDX, value=order)
    param.save()
        
    return s

create_survey()