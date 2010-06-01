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

SUBJECTS = [{"name":"Neil", "number":"1001"}, {"name":"Marisa", "number":"5303044777"}]
SURVEYS = [{"name":"Expert_Strong", "dialstring_prefix":"user/"}, {"name":"Expert_Weak", "dialstring_prefix":"user/"}, {"name":"Peer_Strong", "dialstring_prefix":"user/"}, {"name":"Peer_Weak", "dialstring_prefix":"user/"}]
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
    for survey in SURVEYS:
        if Survey.objects.filter(name=survey["name"]).count() == 0:
            s = Survey(name=survey["name"], dialstring_prefix=survey["dialstring_prefix"])
            s.save()
            count = count + 1
    
    print(str(count) + " new surveys added")

def prompts():
    count = 0
    for survey in Survey.objects.all():
        for prompt in PROMPTS:
            if Prompt.objects.filter(file__contains=prompt["file"], survey=survey).count() == 0:
                p = Prompt(file="en/" + survey.name + "_" + prompt["file"], order=prompt["order"], bargein=prompt["bargein"], survey=survey)
                p.save()
                count = count + 1
                if "options" in prompt:
                    options = prompt["options"]
                    for option in options:
                        o = Option(number=option["number"], action=option["action"], prompt=p)
                        if "action_param1" in option:
                            o.action_param1 = option["action_param1"]
                        if "action_param2" in option:
                            o.action_param1 = option["action_param2"]
                        o.save()
                        
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
