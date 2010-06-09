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
from otalo.surveys.models import Subject, Survey, Call, Prompt, Option
from datetime import datetime

# These should be consistent with the constants
# in survey.lua
OPTION_NEXT = 1
OPTION_PREV = 2
OPTION_REPLAY = 3
OPTION_GOTO = 4

PREFIX = "user/"

SUBJECTS = [{"name":"Neil", "number":"1001"}, {"name":"Marisa", "number":"5303044777"}]
SOURCES = ["E1", "E2", "P1", "P2"]
MSGS = ["T1", "T2", "T3", "T4"]
MSG_TYPES = ["Strong", "Weak"]
BEH_TYPES = ["BCALL", "BHOLD"]
PROMPTS  = [{"file":"welcome.wav", "order":1, "bargein":False, "options":[{"number": "", "action":OPTION_NEXT}]}, {"file":"tip.wav", "order":2, "bargein":False, "options":[{"number": "", "action":OPTION_NEXT}]}, {"file":"confirm.wav", "order":3, "bargein":True, "options":[{"number": "1", "action":OPTION_NEXT}, {"number": "2", "action":OPTION_PREV}, {"number": "", "action":OPTION_REPLAY} ]}, {"file":"behavior.wav", "order":4, "bargein":True, "options":[{"number": "1", "action":OPTION_GOTO, "action_param1":2}, {"number": "", "action":OPTION_REPLAY} ]}]

def subjects():
    count = 0
    for subject in SUBJECTS:
        if Subject.objects.filter(name=subject["name"]).count() == 0:
            s = Subject(name=subject["name"], number=subject["number"])
            s.save()
            count = count + 1
    
    print(str(count) + " new subjects added")

def surveys():    
    count = 0
    for source in SOURCES:
        for msg in MSGS:
            for mtype in MSG_TYPES:
                for btype in BEH_TYPES:
                    surname = source + "_" + msg + "_" + mtype + "_" + btype
                    if Survey.objects.filter(name=surname).count() == 0:
                        s = Survey(name=surname, dialstring_prefix=PREFIX)
                        s.save()
                        count = count + 1
    print(str(count) + " new surveys added")

def prompts():
    count = 0
    for survey in Survey.objects.all():
        # do this instead of prompt check in case there is a change
        # in the order or contents of prompts
        survey.prompt_set.all().delete()
        surveyname = survey.name
        
        # welcome
        welcome = Prompt(file="en/welcome.wav", order=1, bargein=False, survey=survey)
        welcome.save()
        welcome_opt = Option(number="", action=OPTION_NEXT, prompt=welcome)
        welcome_opt.save()
        count = count + 1
        
        # tip
        tfilename = "en/" + surveyname[:surveyname.index("_B")] + "_tip.wav"
        tip = Prompt(file=tfilename, order=2, bargein=False, survey=survey)
        tip.save()
        tip_opt = Option(number="", action=OPTION_NEXT, prompt=tip)
        tip_opt.save()
        count = count + 1
        
        # confirm
        confirm = Prompt(file="en/confirm.wav", order=3, bargein=True, survey=survey)
        confirm.save()
        confirm_opt1 = Option(number="1", action=OPTION_NEXT, prompt=confirm)
        confirm_opt1.save()
        confirm_opt2 = Option(number="2", action=OPTION_PREV, prompt=confirm)
        confirm_opt2.save()
        confirm_opt3 = Option(number="", action=OPTION_REPLAY, prompt=confirm)
        confirm_opt3.save()
        count = count + 1

        # behavior
        tidx = surveyname.index('T')
        tid = surveyname[tidx+1:tidx+2]
        bfilename = "en/behavior" + tid[0]
        if (surveyname.find('HOLD') > -1):
            bfilename += "H.wav"
        else:
            bfilename += ".wav"
        behavior = Prompt(file=bfilename, order=4, bargein=True, survey=survey)
        behavior.save()
        behavior_opt1 = Option(number="1", action=OPTION_GOTO, action_param1=2, prompt=behavior)
        behavior_opt1.save()
        count = count + 1
                        
    print(str(count) + " new prompts added")
                  
def calls():
    count = 0
    d = datetime.now()
    for subject in Subject.objects.all():
        for survey in Survey.objects.all():
            if Call.objects.filter(subject=subject, survey=survey).count() == 0:
                c = Call(subject=subject, survey=survey, date=d, priority=1)
                c.save()
                count = count + 1
                
    print(str(count) + " new calls added")
    
def main():
    subjects()
    surveys()
    prompts()
    calls()
    
main()
