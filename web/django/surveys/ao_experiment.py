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
from otalo.surveys.models import Survey, Subject, Call, Prompt, Option
from random import shuffle

# These should be consistent with the constants
# in survey.lua
OPTION_NEXT = 1
OPTION_PREV = 2
OPTION_REPLAY = 3
OPTION_GOTO = 4

PREFIX = "openzap/smg_prid/a/"
SUFFIX = "@g2"
SOUND_EXT = ".mp3"
REMINDER_NAME = "REMINDER"

SOURCES = ["E1", "E2", "P1", "P2"]
MSGS = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"]
BEH_TYPES = ["BPRESS", "BCALL", "BHOLD"]

INBOUND_PREFIX = "793014"
INBOUND_SUFFIX_START = 2001
INBOUND = {}
#EITHER = [9979403085,9879677274,9979254830,9924057403,9879417564,9558576090,9824387276,9727304678,9727281248,9726488991,9725317885,9723202471,9714174065,9712410421,9624235420,9510748795,9429260174,9429122745,9428897286,9428485487,9428459215,9427258722,9427037241,8140128125,9998750661,9979780231]
#AM = []
#PM = [9978171686, 9913461992]
EITHER = [2877222260,9723037029,9624820573,9726766913,2742295194,9327572297,9978063662,9925795859,9974572646,9913127379,9909484864,9909480769,9909397629,9904689792,9904075323,9898836049,9898533546,9879732707,9879350157,9825875631,9909189931,9726660105,9725729441,9714560511,9714327015,9714246198,9624086950,9574978416,9574416890,9574188431,9429352624,9227352190,9904622685,9824262550,9428671603,9723332236,9426373684,9428500591,9925525663,9426554773,9979711961,9979087320,9714001359,9427535277,9428984533,9726485205,9724632394,9978719704,9924284505,9725850145,8140252102,9979273464,9909621073,9879841603,9879069329,9825524687,9825279001,9726883910,9737369863,9737694692,9824784871,9879274611,9825951687,9723149575]
AM = [9925546520,7567331806,2737236315,9998952575,9974540063,9913921466,9925716672,9723800850,9726331577,9429251501,9228816198,9099514664,9904259110,9909840752,9428136567,9428063295,8000688598,9998088731,9925880755,9924584010,9913657611,9624372044,9909233817,9574013934,9327538732,9725331043,9979459741,9723181832,9974541880,9909893827,9712756833]
PM = [9726051598,9909839117,9428557642,9924500374,9825578331,9824171748,9724700753,9714934982,9925513984,9427379911,2697342397,9428126906,9016249969,9924341087,9909759893,9724884238,8140437612,2833295141,7567164618,9925364656,9913398273,9601567245,9586132465,9426320340,9998318554,9624045636,9978173169,9925660140,9825726214,9727696899,9726814182,9638346557,8980271921,9925583401,9712198296,9824367539,9724443284,9427249401,9016840997,8141847594,9913991823,9893966806,9979314531,9724581388,9624451766,9913332272,9427555857,9638660663,9924355148,9427564859,9974484853,9925145434,9924528796,9913422018,9912011936,9909492653,9909399897,9909070236,9904622512,9726592964,8140255231,2744253277,9726061931,9428987491,9428241676,9979625862,9879876394,9974961909,9974122869,9925310504,9824829592,9924885762,9924773951,9737232762,9725102377,9724774625,9714959731,9714736647,9714148023,9687433392,9624779381,9601145413,9586312853,9904001667,9537559883,9537293638,9429943304,9429609357,9429527617,9228064441,8140877835,9925684373,9687193246,9974669323,9714785932,9638844584,9998664234,9723887815,9427145486,9974641216,9978163140,9429269788,9276502212,9978564476,9879318158,9586058070,9925316417,9924834046,9427667496,9727281416,9974852923,9925618145,9427330743,9978305087,9978383329,9727128162,9904634418,9726356814,9429140966,9879337160,9428568904,9724537977,9638391892,9099193500,9726659436,9723658772,9429218227,9016638646,9925508550,9327477984,9913282079,9913213272,9909847737,9904925740,9904575420,9825378326,9726046695,9726186380,9726477492,9726489610,9726665628,9879879905,9727281261,9727608301,9727641947,9727642827,9727689590,9727696645,9737362944,9737389044,9737583425,9737871915,9824241614,9824928848,9824992905,9879632462,9879319268,9879188943,9879099378,9879044080,9879022533,9825336919,9824967764,9737622557,9737386565,9737125763,9727307784,9726668506,9726592014,9726492370,9726406074,9726384118,9726324249,9725061283,9725040752,9724522159,9723684923,9723011177,9638099359,9726074838,9727424483,9727722178]

GROUPS = [["REMINDER_DUMMY","E1","E2","P1","P2","E1","P1","E2","P2"], ["REMINDER_DUMMY","E2","E1","P2","P1","E2","P2","E1","P1"], ["REMINDER_DUMMY","P1","P2","E1","E2","P1","E1","P2","E2"], ["REMINDER_DUMMY","P2","P1","E2","E1","P2","E2","P1","E1"]]
# prompts for all of these surveys will get created
SURVEYS = ["T1_BCALL", "T2_BCALL", "T3_BCALL", "T4_BCALL", "T5_BCALL", "T6_BCALL", "T7_BCALL", "T8_BHOLD", "T1_BPRESS", "T2_BPRESS", "T3_BPRESS", "T4_BPRESS", "T5_BPRESS", "T6_BPRESS", "T7_BPRESS", "T8_BPRESS"]

def subjects():
    count = 0
    
    all = EITHER + AM + PM
    group_assignment = 0;
    for number in all:
        s = Subject.objects.filter(number = number)
        if not bool(s):
            s = Subject(number=str(number), group=group_assignment)
            print ("adding subject " + str(s))
            s.save()
            group_assignment += 1
            if group_assignment == len(GROUPS):
                group_assignment = 0
            count += 1
    
    print(str(count) + " new subjects added.")
    
def surveys():    
    count = 0
    for source in SOURCES:
        for msg in MSGS:
            for btype in BEH_TYPES:
                surname = source + "_" + msg + "_" + btype
                s = Survey.objects.filter(name=surname)
                if not bool(s):
                    s = Survey(name=surname, dialstring_prefix=PREFIX, dialstring_suffix=SUFFIX, complete_after=2)
                    print ("adding survey " + str(s))
                    s.save()
                    count = count + 1
    
    print(str(count) + " new surveys added")
    prompts()

def prompts():
    count = 0
    
    surveys = []
    for surname in SURVEYS:
        surveys += Survey.objects.filter(name__contains=surname)
            
    # iterate through all outbound surveys only
    for survey in surveys:
        # do this instead of prompt check in case there is a change
        # in the order or contents of prompts
        survey.prompt_set.all().delete()
        surveyname = survey.name
        
        # welcome
        welcome = Prompt(file="guj/welcome" + SOUND_EXT, order=1, bargein=False, survey=survey)
        welcome.save()
        welcome_opt = Option(number="", action=OPTION_NEXT, prompt=welcome)
        welcome_opt.save()
        count = count + 1
        
        # tip
        tfilename = "guj/" + surveyname[:surveyname.index("_B")] + "_tip" + SOUND_EXT
        tip = Prompt(file=tfilename, order=2, bargein=False, delay=0, survey=survey)
        tip.save()
        tip_opt = Option(number="", action=OPTION_NEXT, prompt=tip)
        tip_opt.save()
        count = count + 1

        # behavior
        bfilename = "guj/behavior" + SOUND_EXT
        behavior = Prompt(file=bfilename, order=3, bargein=False, delay=0, survey=survey)
        behavior.save()
        beh_opt = Option(number="", action=OPTION_NEXT, prompt=behavior)
        beh_opt.save()
        count = count + 1
        
        # Action step prompt
        btypeidx = surveyname.index('B')
        btype = surveyname[btypeidx+1:btypeidx+2]
        # special behavior for the press button for more info behavior
        if btype == 'P':
            action = Prompt(file="guj/press" + SOUND_EXT, order=4, bargein=False, delay=0, survey=survey)
            action.save()
            action_opt = Option(number="", action=OPTION_NEXT, prompt=action)
            action_opt.save()
            count = count + 1
            
            repeat = Prompt(file="guj/repeat" + SOUND_EXT, order=5, bargein=True, delay=3000, survey=survey)
            repeat.save()
            repeat_opt1 = Option(number="1", action=OPTION_NEXT, prompt=repeat)
            repeat_opt1.save()
            repeat_opt2 = Option(number="2", action=OPTION_GOTO, action_param1=2, prompt=repeat)
            repeat_opt2.save()
            count = count + 1
            
            # solution confirm
            oksolution = Prompt(file="guj/oksolution" + SOUND_EXT, order=6, bargein=False, survey=survey)
            oksolution.save()
            oksoln_opt = Option(number="", action=OPTION_NEXT, prompt=oksolution)
            oksoln_opt.save()
            count = count + 1
            
            # solution
            sfilename = "guj/" + surveyname[:surveyname.index("_B")] + "_solution" + SOUND_EXT
            solution = Prompt(file=sfilename, order=7, bargein=False, survey=survey)
            solution.save()
            soln_opt = Option(number="", action=OPTION_NEXT, prompt=solution)
            soln_opt.save()
            count = count + 1
            
            # followup
            followup = Prompt(file="guj/followup" + SOUND_EXT, order=8, bargein=True, survey=survey)
            followup.save()
            followup_opt = Option(number="", action=OPTION_GOTO, action_param1=6, prompt=followup)
            followup_opt.save()
            count = count + 1
        elif btype == 'C':
            action = Prompt(file="guj/call" + SOUND_EXT, order=4, bargein=False, delay=0, survey=survey)
            action.save()
            action_opt = Option(number="", action=OPTION_NEXT, prompt=action)
            action_opt.save()
            count = count + 1
            
            # phone num
            tipidx = surveyname.index('T')
            tip = surveyname[:surveyname.index('_',tipidx)]
            numfile = INBOUND[tip]
            phonenum = Prompt(file="guj/" + numfile + SOUND_EXT, order=5, bargein=False, delay=0, survey=survey)
            phonenum.save()
            phonenum_opt = Option(number="", action=OPTION_NEXT, prompt=phonenum)
            phonenum_opt.save()
            count = count + 1
            
            repeat = Prompt(file="guj/repeat" + SOUND_EXT, order=6, bargein=True, delay=1000, survey=survey)
            repeat.save()
            repeat_opt1 = Option(number="", action=OPTION_GOTO, action_param1=3, prompt=repeat)
            repeat_opt1.save()
            repeat_opt2 = Option(number="2", action=OPTION_GOTO, action_param1=2, prompt=repeat)
            repeat_opt2.save()
            count = count + 1
        elif btype == 'H':
            # hold
            action = Prompt(file="guj/hold" + SOUND_EXT, order=4, bargein=False, delay=0, survey=survey)
            action.save()
            action_opt1 = Option(number="", action=OPTION_NEXT, prompt=action)
            action_opt1.save()
            action_opt2 = Option(number="2", action=OPTION_GOTO, action_param1=2, prompt=action)
            action_opt2.save()
            count = count + 1
            
            # solution
            sfilename = "guj/" + surveyname[:surveyname.index("_B")] + "_solution" + SOUND_EXT
            solution = Prompt(file=sfilename, order=5, bargein=False, survey=survey)
            solution.save()
            soln_opt = Option(number="", action=OPTION_NEXT, prompt=solution)
            soln_opt.save()
            count = count + 1
            
            # followup
            followup = Prompt(file="guj/followup" + SOUND_EXT, order=6, bargein=True, survey=survey)
            followup.save()
            followup_opt = Option(number="", action=OPTION_GOTO, action_param1=5, prompt=followup)
            followup_opt.save()
            count = count + 1
                        
    print(str(count) + " new prompts added")
    
def inbound_surveys():
    count = 0
    for source in SOURCES:
        for msg in MSGS:
            surname = source + "_" + msg + "_inbound"
            number = INBOUND[source + "_" + msg]
            s = Survey.objects.filter(name=surname)
            if not bool(s):
                s = Survey(name=surname, dialstring_prefix=PREFIX, dialstring_suffix=SUFFIX, number=number, complete_after=1)
                print ("adding inbound survey " + str(s))
                s.save()
                count = count + 1
    
    print(str(count) + " new inbound surveys added")
    inbound_prompts()
    
def inbound_prompts():
    count = 0
    # iterate through all inbound surveys only
    for survey in Survey.objects.filter(number__isnull=False):
        # do this instead of prompt check in case there is a change
        # in the order or contents of prompts
        survey.prompt_set.all().delete()
        surveyname = survey.name
        
        # solution confirm
        oksolution = Prompt(file="guj/oksolution" + SOUND_EXT, order=1, bargein=False, survey=survey)
        oksolution.save()
        oksoln_opt = Option(number="", action=OPTION_NEXT, prompt=oksolution)
        oksoln_opt.save()
        count = count + 1
        
        # solution
        sfilename = "guj/" + surveyname[:surveyname.index("_inbound")] + "_solution" + SOUND_EXT
        solution = Prompt(file=sfilename, order=2, bargein=False, survey=survey)
        solution.save()
        soln_opt = Option(number="", action=OPTION_NEXT, prompt=solution)
        soln_opt.save()
        count = count + 1
        
        # followup
        followup = Prompt(file="guj/followup" + SOUND_EXT, order=3, bargein=True, survey=survey)
        followup.save()
        followup_opt = Option(number="", action=OPTION_PREV, prompt=followup)
        followup_opt.save()
        count = count + 1
        
    print(str(count) + " new inbound prompts added")   

def reminder_survey():
    count = 0

    s = Survey.objects.filter(name=REMINDER_NAME)
    if not bool(s):
        s = Survey(name=REMINDER_NAME, dialstring_prefix=PREFIX, dialstring_suffix=SUFFIX, complete_after=1)
        print ("adding reminder survey " + str(s))
        s.save()
        
        reminder_prompt = Prompt(file="guj/reminder" + SOUND_EXT, order=1, bargein=False, delay=0, survey=s)
        reminder_prompt.save()
        count = count + 1
    
    print(str(count) + " new reminder survey added")

def shift_calls(starting, timeshift):
    calls = Call.objects.filter(date__gte=starting)
    
    for call in calls:
        print ("shifting " + str(call) + " to date " + str(call.date + timeshift))
        call.date += timeshift
        call.save()

#to_change of the form {"TX_BY":"TR_BS", ... }
def change_surveys(to_change):
    for oldname,newname in to_change.items():
        olds = Survey.objects.filter(name__contains=oldname)
        for old in olds:
            #get source
            source = old.name[:old.name.index('_')]
            # get new
            new = Survey.objects.get(name=source+'_'+newname)
            calls = Call.objects.filter(survey=old)
            for call in calls:
                print("changing call " + str(call) + " to have survey " + str(new))
                call.survey = new
                call.save()
def main():
    # create inbound number assignments
    suffix = INBOUND_SUFFIX_START
    for source in SOURCES:
        for msg in MSGS:
            surname = source + "_" + msg
            INBOUND[surname] = INBOUND_PREFIX + str(suffix)
            suffix += 1
            
    subjects()
    surveys()
    #inbound_surveys()
    #reminder_survey()
    
    #shift_start = datetime(year=2010, month=8, day=2)
    #oneday = timedelta(days=1)
    #shift_calls(shift_start, oneday)
    #changes = {"T7_BCALL":"T7_BPRESS"}
    #change_surveys(changes)

main()

