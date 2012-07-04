import os, sys
from datetime import datetime, timedelta
from openpyxl.reader.excel import load_workbook
from django.contrib.auth.models import User as AuthUser
from django.conf import settings
from django.db.models import Count
from otalo.ao.models import User, Line, Forum, Message_forum, Membership, Admin
from otalo.surveys.models import Subject, Survey, Prompt, Option, Call, Param, Input
from otalo.sms.models import Config as SMSConfig, ConfigParam
from otalo.sms import sms_utils

'''
****************************************************************************
******************* CONSTANTS **********************************************
****************************************************************************
'''
MAX_MSG_LEN_SECS = 60
STREAMIT_LINE_DESIGNATOR = "_STREAMIT"

PROFILES = {'freetdm/grp1/a/0':{'basenum':7961907720, 'maxnums':2, 'maxparallel':30}}

INTERVAL_MINS = 10
# Should be AT LEAST the interval, or else 
# A broadcast could be missed to get scheduled
BUFFER_MINS = INTERVAL_MINS + 0
SMS_DELAY_MINS = 0

SMS_DEFAULT_CONFIG_FILE='sms.conf'
        
STREAMIT_FILE_DIR = '/home/awaazde/otalo/ao/'
STREAMIT_GROUP_LIST_FILENAME = 'groups.xlsx'
        
SOUND_EXT = '.wav'
STREAMIT_SOUNDS_DIR = '/usr/local/freeswitch/scripts/streamit/sounds/'

STREAMIT_SIGNUP_INFO = '8866123453'
SMS_INVITE_TEXT = {"eng": "%s invites you to join the %s group. Call %s to subscribe. Send your voice to your own groups: "+STREAMIT_SIGNUP_INFO, "hin": "%s invites you to join the %s group. Call %s to subscribe. Send your voice to your own groups: "+STREAMIT_SIGNUP_INFO}
SMS_MESSAGE_TEXT = {"eng": "New message from %s (%s)! Call %s to listen. Send your voice to your own groups: "+STREAMIT_SIGNUP_INFO, "hin": "New message from %s (%s)! Call %s to listen. Send your voice to your own groups: "+STREAMIT_SIGNUP_INFO }


'''
****************************************************************************
******************* GROUP MANAGEMENT ***************************************
****************************************************************************
'''

def update_user(name, number):
    user = User.objects.filter(number=number)
    if bool(user):
        user = user[0]
        user.name = name
        user.save()
        print ("Updating user "+str(user))
    else:
        user = User.objects.create(name=name, number=number, allowed='y')
        print("Creating user "+str(user))
    
    return user

def update_group(groupname, owner, lang, status=Forum.STATUS_BCAST_CALL_SMS):
    group = Forum.objects.filter(name=groupname, admin__user=owner)
    if bool(group):
        group = group[0]
        group.name_file = groupname.replace(' ','').lower() + SOUND_EXT
        group.moderated = 'n'
        group.posting_allowed = 'n'
        # Allow responses by default
        group.responses_allowed = 'y'
        group.routeable = 'n'
        group.maxlength = MAX_MSG_LEN_SECS
        group.max_user_resp_len = MAX_MSG_LEN_SECS
        group.status = status
        group.save()
        
        line = group.line_set.all()[0]
        line.name = get_line_name(group)
        line.language = lang
        line.save()
        print("Updating group "+ str(group))
    else:
        group = Forum.objects.create(name=groupname, name_file = groupname.replace(' ','').lower() + SOUND_EXT, moderated='n', posting_allowed='n', responses_allowed='y',routeable='n',maxlength=MAX_MSG_LEN_SECS,max_user_resp_len = MAX_MSG_LEN_SECS, status=status )
        
        # create Auth
        auth = Admin.objects.filter(user=owner)
        if bool(auth):
            auth = auth[0].auth_user
        else:
            username = owner.name.split(' ')[0].lower()
            unamecount = AuthUser.objects.filter(username=username).count()
            if unamecount > 0:
                username += str(unamecount+1)
            password = username+'123'
            auth = AuthUser.objects.create(username=username, password=password)
            print ("Creating Auth "+str(auth))
        
        # create Admin
        admin = Admin.objects.create(user=owner, forum=group, auth_user=auth)
        print ("Creating Admin "+str(admin))
        
        # create Line
        number = generate_line_number()
        info = load_sms_config_info()
        config = SMSConfig.objects.filter(url=info['url'])
        if bool(config):
            config = config[0]
        else:
            config = SMSConfig.objects.create(url=info['url'], to_param_name=info['to'], text_param_name=info['text'], date_param_name=info['date'], date_param_format=info['dateformat'], country_code=info['countrycode'])
            ConfigParam.objects.create(name='feedid', value=info['feedid'], config=config)
            ConfigParam.objects.create(name='username', value=info['username'], config=config)
            ConfigParam.objects.create(name='password', value=info['password'], config=config)
            
        name = get_line_name(group)
        line = Line.objects.create(name=name, number=number, language=lang, callback=False, sms_config=config)
        line.forums.add(group)
        print("Creating Line "+str(line))
        
        print("Creating Group "+str(group))
    
    return group

def update_groups_by_file(groups_file = None):
    if groups_file is None:
        groups_file = STREAMIT_FILE_DIR + STREAMIT_GROUP_LIST_FILENAME
    wb = load_workbook(filename = groups_file)
    
    user_info = wb.get_sheet_names()
    
    for info in user_info:
        sht = wb.get_sheet_by_name(info)
        info = info.split('-')
        info = [elt.strip() for elt in info]
        name = info[0]
        number = info[1]
        lang = info[2]
        status = info[3]
        if status == "sms":
            status = Forum.STATUS_BCAST_SMS
        else:
            status = Forum.STATUS_BCAST_CALL_SMS
            
        owner = update_user(name, number)
        
        groups_found = [] 
        for col in sht.columns:
            line = [str(cell.value) for cell in col]
            groupname = line[0]
            line = line[1:]
            print("line is "+str(line))
            g = update_group(groupname, owner, lang, status)
            
            members = []
            for number in line:
                if number != 'None' and number != '':
                    print("number is "+str(number))
                    number = number[-10:]
                    user = User.objects.filter(number=number)
                    if bool(user):
                        user = user[0]
                    else:
                        user = User.objects.create(number=number, allowed='y')
                    members.append(user)
            update_members(g, members)
            
            groups_found.append(g.id)
        
        to_deactivate = Forum.objects.filter(line__name__contains=STREAMIT_DESIGNATOR, admin__user=owner).exclude(status=Forum.STATUS_INACTIVE).exclude(pk__in=groups_found)
        for group in to_deactivate:
            print("De-activating group "+str(group))
            group.status = Forum.STATUS_INACTIVE
            group.save()

'''
    Treat the member list as the entire group of new members
    (i.e. delete people not in this list who were previously
    in the group)
'''
def update_members(group, members, sendinvite=True, status=Membership.STATUS_UNCONFIRMED):
    to_invite=[]
    for member in members:
        membership = Membership.objects.filter(group=group, user=member)
        if not bool(membership):
            membership = Membership.objects.create(group=group, user=member, status=status)
            to_invite.append(member)
            print("Adding membership "+str(membership))
        else:
            membership = membership[0]
            membership.status = status
            membership.save()
            print("Updating membership "+str(membership))
    
    to_delete = Membership.objects.filter(group=group).exclude(user__in=members)
    for member in to_delete:
        print("Deleting member "+str(member))
        member.status = Membership.STATUS_DELETED
        member.save()
    
    if sendinvite and to_invite:
        send_invite_sms(group,to_invite)

'''
    This incrementally add/updates membership without 
    messing with the original members
'''
def add_member(group, number, sendinvite=True, status=Membership.STATUS_UNCONFIRMED):
    user = User.objects.filter(number=number)
    if bool(user):
        user = user[0]
    else:
        user = User.objects.create(number=number, allowed='y')
    
    membership = Membership.objects.filter(group=group, user=user)
    if not bool(membership):
        membership = Membership.objects.create(group=group, user=member, status=status)
        print("Adding membership "+str(membership))
        
        if sendinvite:
           send_invite_sms(group,[user]) 
    else:
        membership = membership[0]
        membership.status = status
        membership.save()
        print("Updating membership "+str(membership))
'''
****************************************************************************
************************** CALL SCHEUDLING *********************************
****************************************************************************
'''
   
'''
    This function is meant to wake up every
    INTERVAL_MINS and create any bcasts that were
    posted since it last ran 
'''     
def create_bcasts(interval = None):
    if interval is None:
        interval = get_most_recent_interval()
      
    # create any bcasts that were posted in last INTERVAL MINS
    messagesf = Message_forum.objects.filter(forum__line__name__contains=STREAMIT_LINE_DESIGNATOR, message__date__gt=interval-timedelta(minutes=INTERVAL_MINS))
    print("Found msgs to create bcasts since last interval: "+str(messagesf))
    for messagef in messagesf:
        create_bcast_survey(messagef)
        
'''
    This function is meant to wake up every
    INTERVAL_MINS and run scheduling
    algorithm on all pending bcasts
'''
def schedule_bcasts(bcasttime = None):
    if bcasttime is None:
        bcasttime = get_most_recent_interval()
        # add buffer time
        bcasttime += timedelta(minutes=BUFFER_MINS)
        
    print("Scheduling bcasts for time: "+ time_str(bcasttime))
    
    # gather all bcasts pending as of bcasttime
    # This is a comparison between group recipients and calls scheduled
    num_pending = {}
    for group in Forum.objects.filter(line__name__contains=STREAMIT_LINE_DESIGNATOR, status=Forum.STATUS_BCAST_CALL_SMS):
        bcastcount = group.members.filter(membership__status=Membership.STATUS_SUBSCRIBED).count()
        #print("for group, "+str(group)+" num members: "+str(bcastcount))
        number = get_line_number(group)
        pending_bcasts = Survey.objects.annotate(num_scheduled=Count("call")).filter(number=number, broadcast=True, num_scheduled__lt=bcastcount)
        for bcast in pending_bcasts:
            #print("pending bcast: "+ str(bcast))
            scheduled_subjs = Call.objects.filter(survey=bcast).values('subject__number')
            to_sched = group.members.exclude(number__in=scheduled_subjs)
            #print("to schedule: "+ str(to_sched))
            num_pending[bcast] = [bcastcount - bcast.num_scheduled, to_sched]
    
    # Implementing Shortest Remaining Finish Time discipline (though non-preemptive)
    # sort the list in descending order of num_pending
    sorted_bcasts = sorted(num_pending.iteritems(), key=lambda pair: pair[1][0], reverse=True)
    # sorted_bcast is a list of tuples: [(s1, [5, [u1,u2,u3,u4,u5]]), (s2, [2, [u6,u7]]), ...]
    # now flatten it out to just get bcast-user pairs
    flat = []
    for s,users in sorted_bcasts:
        for u in users[1]:
            flat.append([s,u])
            
    #print("sorted list: "+str(flat))       
    
    # assign calls as they are
    # found to be available
    i = 0
    scheduled = {}
    for prefix in PROFILES:
        num_available = PROFILES[prefix]['maxparallel'] - Call.objects.filter(dialstring_prefix=prefix, date=bcasttime).count()
        #print("prefix "+prefix+" maxpara="+str(PROFILES[prefix]['maxparallel'])+" existing call count="+str(Call.objects.filter(dialstring_prefix=prefix, date=bcasttime).count()))
        to_sched = flat[i:i+num_available]
        for survey, recipient in to_sched:
            subject = Subject.objects.filter(number=recipient.number)
            if bool(subject):
                subject = subject[0]
            else:
                subject = Subject.objects.create(name=recipient.name, number=recipient.number)
            
            call = Call.objects.create(survey=survey, dialstring_prefix=prefix, subject=subject, date=bcasttime, priority=1)
            print('Scheduled call '+ str(call))
            if survey.number in scheduled:
                scheduled[survey.number].append(recipient)
            else:
                scheduled[survey.number]=[recipient]
        i += num_available
    
    if scheduled:
        for linenumber in scheduled:
            group = Forum.objects.get(line__number=linenumber)
            send_message_sms(group, scheduled[linenumber], bcasttime+timedelta(minutes=SMS_DELAY_MINS))
              
def create_and_schedule_bcast(messagef, date=None):
    group = messagef.forum
    if group.status == Forum.STATUS_BCAST_SMS:
        recipients = group.members.filter(membership__status=Membership.STATUS_SUBSCRIBED)
        send_message_sms(group, recipients, date)
    else:
        b = create_bcast_survey(messagef)
        schedule_bcasts(date)
    
def create_bcast_survey(messagef):
    line = messagef.forum.line_set.all()[0]
    language = line.language
    s = Survey.objects.create(name=str(messagef), number=line.number, broadcast=True, complete_after=0)
    print("Creating broadcast "+str(s))
    
    order = 1
    welcome = Prompt(file=STREAMIT_SOUNDS_DIR+language+"/welcome_outbound"+SOUND_EXT, order=order, bargein=True, survey=s, delay=0)
    welcome.save()
    welcome_opt = Option(number="", action=Option.NEXT, prompt=welcome)
    welcome_opt.save()
    welcome_opt2 = Option(number="1", action=Option.NEXT, prompt=welcome)
    welcome_opt2.save()
    order += 1
    
    # content
    content = Prompt(file=settings.MEDIA_ROOT+"/"+messagef.message.content_file, order=order, bargein=True, survey=s)
    content.save()
    content_opt = Option(number="", action=Option.NEXT, prompt=content)
    content_opt.save()
    content_opt2 = Option(number="1", action=Option.NEXT, prompt=content)
    content_opt2.save()
    order += 1
    
    if messagef.forum.responses_allowed == 'y':
        chooserecord = Prompt(file=STREAMIT_SOUNDS_DIR+language+"/chooserecord"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
        chooserecord.save()
        chooserecord_opt = Option(number="", action=Option.GOTO, prompt=chooserecord)
        chooserecord_opt.save()
        param = Param(option=chooserecord_opt, name=Param.IDX, value=order+2)
        param.save()
        chooserecord_opt2 = Option(number="1", action=Option.NEXT, prompt=chooserecord)
        chooserecord_opt2.save()
        order += 1
    
        record = Prompt(file=STREAMIT_SOUNDS_DIR+language+"/pleaserecord"+SOUND_EXT, order=order, bargein=True, survey=s, name='Response' )
        record.save()
        record_opt = Option(number="", action=Option.RECORD, prompt=record)
        record_opt.save()
        param = Param(option=record_opt, name=Param.MFID, value=messagef.id)
        param.save()
        maxlen = messagef.forum.max_user_resp_len or Forum.MAX_USER_RESP_LEN_DEF
        param2 = Param(option=record_opt, name=Param.MAXLENGTH, value=str(maxlen))
        param2.save()
        record_opt2 = Option(number="1", action=Option.RECORD, prompt=record)
        record_opt2.save()
        param3 = Param(option=record_opt2, name=Param.MFID, value=messagef.id)
        param3.save()
        param4 = Param(option=record_opt2, name=Param.MAXLENGTH, value=str(messagef.forum.maxlength))
        param4.save()
        order += 1
    else:
        '''
        By default, if not taking recorded responses, take a pause for touchtone
        '''
        input = Prompt(file=STREAMIT_SOUNDS_DIR+"/blank"+SOUND_EXT, order=order, bargein=True, survey=s, name='Response', inputlen=1, delay=4000)
        input.save()
        input_opt = Option(number="", action=Option.NEXT, prompt=input)
        input_opt.save()
    
    # thanks
    thanks = Prompt(file=STREAMIT_SOUNDS_DIR+language+"/thankyou"+SOUND_EXT, order=order, bargein=True, survey=s)
    thanks.save()
    thanks_opt1 = Option(number="", action=Option.NEXT, prompt=thanks)
    thanks_opt1.save()
    
    return s
         
'''
****************************************************************************
************************** UTILS *******************************************
****************************************************************************
'''
        
def get_most_recent_interval():
    interval = datetime.now()
    # round up to nearest minute
    if interval.second != 0 or interval.microsecond != 0:
        interval = datetime(year=interval.year, month=interval.month, day=interval.day, hour=interval.hour, minute=interval.minute)
        interval += timedelta(minutes=1)
        
    # Locate most recent stack of
    # scheduled messages
    for i in range(INTERVAL_MINS-1,-1,-1):
        if bool(Call.objects.filter(date=interval-timedelta(minutes=i))):
            interval -= timedelta(minutes=i)
            break
    print("Found most recent interval: "+time_str(interval)) 
    return interval
    
def get_line_name(group):
    owner = User.objects.get(admin__forum=group)
    return owner.name + "_" + owner.number + STREAMIT_LINE_DESIGNATOR

def get_line_number(group):
    line = group.line_set.all()[0]
    return line.number
     
def generate_line_number():
    for prefix in PROFILES:
        info = PROFILES[prefix]
        base = info['basenum']
        nums = [str(n) for n in range(base,base+info['maxnums'])]
        numlines = Line.objects.filter(number__in=nums).count()
        if numlines < info['maxnums']:
            return str(base + numlines)
        
def load_sms_config_info(file=None):
    if file is None:
        file = SMS_DEFAULT_CONFIG_FILE
    
    info={}
    for line in open(file, "r"):
        k,v = line.strip().split('=')
        info[k] = v
    
    return info

def send_invite_sms(group, to_send, send_date=None):
    print("Sending Invite SMS " + str(group) + ": "+str(to_send))
    send_sms(group,to_send,SMS_INVITE_TEXT,send_date)

def send_message_sms(group, to_send, send_date=None):
    print("Sending Message SMS " + str(group) + ": "+str(to_send))
    send_sms(group,to_send,SMS_MESSAGE_TEXT,send_date)
    
def send_sms(group, to_send, content_dict, send_date):
    line = group.line_set.all()[0]
    text = content_dict[line.language]
    owner = User.objects.get(admin__forum=group)
    text = text % (owner.name, group.name, line.number)
    sms_utils.send_sms(group.line_set.all()[0], to_send, text, send_date, owner)
    
def time_str(date):
    #return date.strftime('%Y-%m-%d')
    return date.strftime('%m-%d-%y %H:%M')
  
'''
****************************************************************************
*************************** MAIN *******************************************
****************************************************************************
'''

if __name__=="__main__":
    if "--schedule_bcasts" in sys.argv:
        schedule_bcasts()
    elif "--update_groups_by_file" in sys.argv:
        update_groups_by_file()
    elif "--schedule_bcast" in sys.argv:
        mfid = sys.argv[2]
        mf = Message_forum.objects.get(pk=mfid)
        create_and_schedule_bcast(mf)
    elif "--add_member" in sys.argv:
        groupid = sys.argv[2]
        number = sys.argv[3]
        group = Forum.objects.get(pk=groupid)
        add_member(group, number)
    else:
        print("Command not found.")