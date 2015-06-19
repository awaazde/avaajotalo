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
import os, stat, re, math
from decimal import Decimal
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from otalo.ao.models import Line, Forum, Message, Message_forum, User, Tag, Forum_tag, Message_responder, Admin, Membership
from otalo.surveys.models import Survey, Prompt, Input, Call, Option
from otalo.sms.models import SMSMessage
from otalo.sms import sms_utils
from django.core import serializers
from django.conf import settings
from django.db.models import Min, Max, Count, Q
from datetime import datetime, timedelta
from django.core.servers.basehttp import FileWrapper
import json
import broadcast
import otalo_utils, stats_by_phone_num
import subprocess
from itertools import chain
from operator import attrgetter
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery
from haystack.query import SQ
from django.contrib.messages.context_processors import messages
from django.core.paginator import Paginator
from django.contrib.admin.templatetags.admin_list import results
import subprocess
from otalo.utils import sync_utils

# Only keep these around as legacy
MESSAGE_STATUS_PENDING = Message_forum.STATUS_PENDING
MESSAGE_STATUS_APPROVED = Message_forum.STATUS_APPROVED
MESSAGE_STATUS_REJECTED = Message_forum.STATUS_REJECTED

# Routing Constants
MAX_RESPONDERS = 5
MIN_RESPONDERS = 2
MAX_QUESTIONS_PER_RESPONDER = 10
# should match common.lua
LISTEN_THRESH = 5
# This variable should be consistent with MessageList.java
VISIBLE_MESSAGE_COUNT = 10

# Validation error codes
INVALID_NUMBER = "1"
NO_CONTENT = "2"
INVALID_GROUPNAME = "3"
MEMBER_CREDITS_EXCEEDED = "4"
INVALID_DATE = "5"
INVALID_GROUP_SETTING = "6"
INVALID_FILE_FORMAT = "7"
MAX_GROUPS_REACHED = "8"
NOT_ENOUGH_BALANCE = "9"


#Tags related constants
#This is separator for all the selected tags. From the client side, all the selected tags are coming with this seperatar.
#Also this constant must be consistent with the same constant in AutoCompleteWidget.java 
TAG_SEPERATOR = "##"
#These search related constants must be consistent with the same constant in JSONRequest.AoAPI.SearchConstants class.
SEARCH_PARAM = "search_data"
SEARCH_KEYWORD = "search_keyword"
STATUS = "status"
FROMDATE = "fromDate"
TODATE = "toDate"
TAG = "tags"
AUTHOR = "author"

AUTHOR_NAME = "author_name"
AUTHOR_NUMBER = "author_number"
AUTHOR_DISTRICT = "author_district"
AUTHOR_TALUKA = "author_taluka"
AUTHOR_VILLAGE = "author_village"
STATUS_RESPONDED = "3"
SEARCH_PARAM_FORUM = "forum"


# this will be used to get the page from result
PAGE_PARAM = "result_page"

# How many bcasts to display at a time
BCAST_PAGE_SIZE = 10

SMS_LENGTH = 160
# corresponds to enum in SMSList.java
SMSListType_IN = 0
SMSListType_SENT = 1

@login_required
def index(request):
    #return render_to_response('AO/index.html', {'fora':fora})
    
    if 'show' not in request.GET:
        auth_user = request.user
        user = User.objects.filter(admin__auth_user=auth_user).distinct()
        if user.exists() and user[0].no_login == 1:
            groups = Forum.objects.filter(admin__auth_user=auth_user).exclude(status=Forum.STATUS_INACTIVE).distinct()
            numbers = Line.objects.get(forums__admin__auth_user=auth_user, forums=groups[0])
            return render(request, 'registration/welcome.html', {'group_name': groups[0].name, 'group_number': numbers.number})
        
    return render_to_response('Ao.html')
    

def forum(request):
    auth_user = request.user
    
    if not auth_user.is_superuser:
        # get all forums that this user has access to
        fora = Forum.objects.filter(admin__auth_user=auth_user).exclude(status=Forum.STATUS_INACTIVE).distinct()
    else:
        fora = Forum.objects.all()
        
    return send_response(fora, excludes=('messages','tags','responders', 'members'))

def group(request):
    auth_user = request.user
    params = request.GET
    
    if not auth_user.is_superuser:
        # get all forums that this user has access to
        if 'forums' in params and bool(params['forums']):
            groups = Forum.objects.filter(admin__auth_user=auth_user).exclude(status=Forum.STATUS_INACTIVE).distinct()
        else:
            groups = Line.objects.filter(forums__admin__auth_user=auth_user).exclude(forums__status=Forum.STATUS_INACTIVE).distinct().order_by('-id')
    else:
        if 'forums' in params:
            groups = Forum.objects.all()
        else:
            groups = Line.objects.all().order_by('-id')
    
    excludes=()
    relations={}
    if 'forums' in params:
        excludes=('members','messages','tags','responders')
    else:
        relations={'forums':{'relations':{'responders':{'excludes':('name','balance','district','taluka','village','allowed','email','tags','name_file','balance_last_updated','indirect_bcasts_allowed')}}, 'excludes':('members','messages','tags',)}}
        
    return send_response(groups, relations=relations, excludes=excludes )

def messages(request, forum_id):
    params = request.GET
    forum = get_object_or_404(Forum, pk=int(forum_id))
    
    status = params['status'].split()
    posttype = params['posttype']
    
    if posttype == 'top':
        message_forums = Message_forum.objects.filter(forum=forum_id, status__in=status, message__lft=1).order_by('-position', '-message__date')
    elif posttype == 'responses':
        message_forums = Message_forum.objects.filter(forum=forum_id, status__in=status, message__lft__gt=1).order_by('-position', '-message__date')
    elif posttype == 'all':
        message_forums = Message_forum.objects.filter(forum=forum_id, status__in=status).order_by('-position', '-message__date')
    
    count = message_forums.count()  
   
    if params.__contains__('messageforumid'):
        targetid = params['messageforumid']
        found = False
        for start in range(0, count, VISIBLE_MESSAGE_COUNT):
            chunk = message_forums[start:start+VISIBLE_MESSAGE_COUNT]
            for mf in chunk:
                if mf.id == long(targetid):
                    message_forums = chunk
                    found = True
            if found:
                break
            
        if not found:
            # Then this message left the list on a previous action
            # (like moderation), in which case we assume we have
            # been sent the original startIndex
            start = int(params['start'])
            # If the disappeared message was the first on the next page
            # boundary (really should only need to be == comparison),
            # set the start to one page earlier
            if start >= count:
                start -= VISIBLE_MESSAGE_COUNT
                
    else:
        start = int(params['start'])
        # fell off the page
        if start >= count and start > 0:
            start -= VISIBLE_MESSAGE_COUNT
        message_forums = message_forums[start:min(message_forums.count(),start+VISIBLE_MESSAGE_COUNT)]
    
    # if this forum has members, override users' names
    # with membership.membername for display purposes
    if forum.members.all():
        users = [mf.message.user for mf in message_forums]
        memberships = Membership.objects.filter(group=forum, user__in=users)
        membernamedict = {}
        for membership in memberships:
            membernamedict[membership.user] = membership.membername
        for u in users:
            if u in membernamedict:
                # for serialization purposes only; do not save.
                # Use NoneType membernames as well because this is
                # a full overwrite
                u.name = membernamedict[u]
                
    resp = send_response(message_forums, {'message':{'relations':{'user':{'fields':('name', 'number',)}}}, 'forum':{'fields':('name', 'moderated', 'responses_allowed', 'posting_allowed', 'routeable')}})
    
    if count > 0:
        # append some meta info about the messages
        # remove end bracket
        jsonresp = resp.content[:-1]
        jsonresp += ', {"model":"MESSAGE_METADATA", "start":'+str(start)+', "count":'+str(count)+'}]'
        resp.content = jsonresp
        
    return resp

def messageforum(request, message_forum_id):
    # Note use of filter instead of get to return a query set
    message = get_list_or_404(Message_forum, pk=message_forum_id)
    # means don't put any restrictions on the fields returned for forum relation
    return send_response(message, {'message':{'fields':()}, 'forum':{}})

def user(request, user_id):
    # Note use of filter instead of get to return a query set
    user = get_list_or_404(User, pk=user_id)
    return send_response(user)

@csrf_exempt
def updatemessage(request):
    params = request.POST
    
    u = User.objects.get(pk=params['userid'])
    if params['number'] != '':
        u.number = params['number']
    if params['name'] != '':
        u.name = params['name']
    u.district = params['district']
    u.taluka = params['taluka']
    u.village = params['village']

    u.save()   

    m = get_object_or_404(Message_forum, pk=params['messageforumid'])

        
    # Save tags
    selected_tags_input = params['selected_tags']
    m.tags.clear()
    
    if selected_tags_input != '':
        selected_tags = selected_tags_input.split(TAG_SEPERATOR);
        selected_tags = [t.encode('ascii', 'ignore') for t in selected_tags]
        for sel_tag in selected_tags:
            # getting all the tags reference having tag name
            tag_refs = Tag.objects.filter(tag=sel_tag)
            if bool(tag_refs):
                #if existing then taking first one
                tag = tag_refs[0]
            else:
                tag = Tag.objects.create(tag=sel_tag)
            
            m.tags.add(tag)
            #now checking into forum_tags whether this is existing or not    
            forum_tag = Forum_tag.objects.filter(forum=m.forum, tag=tag)
            if not bool(forum_tag):
                Forum_tag.objects.create(forum=m.forum, tag=tag)
            
    
    if m.forum.routeable == 'y':
        # Only run routing algorithm if tags have been updated.
        # But don't override manual setting of responders if they
        # were also made
        responders_changed = int(params['responders_changed'])
        if responders_changed:
            responders = []
            if params.__contains__('responders'):
                responder_ids = params.getlist('responders')
                for responder_id in responder_ids:
                    responder = User.objects.get(pk=responder_id)
                    responders.append(responder)
            
            
            # can take into account previous pass and listen histories
            Message_responder.objects.filter(message_forum=m).delete()
            t = datetime.now()
            for responder in responders:
                mr = Message_responder(message_forum=m, user=responder, assign_date=t)
                mr.save();
    
    # Always calling save on message_forum model when using update_index command for haystack. 
    # It's require because it will trigger post_save signal on it and this signal is being capture by haystack RealtimeSignal processor
    # to update the index data. If we don't call save on it then, on updation of tags or any other many-to-many field data, it won't trigger post_save signal 
    # and so the realtime signal processor won't update index data which would be result in wrong search result.
    #in case if not using rebuild_index command to update index data then this is not required. 
    m.save()
                
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse('otalo.ao.views.messageforum', args=(int(m.id),)))

@csrf_exempt
def movemessage(request):
    params = request.POST
    direction = params['direction']    

    m = get_object_or_404(Message_forum, pk=params['messageforumid'])
    forum_msgs = Message_forum.objects.filter(forum = m.forum, status = MESSAGE_STATUS_APPROVED, message__lft = 1)
    count = forum_msgs.count()
    
    if direction == 'up':
        if m.position and m.position < count:
            # if this msg has a position then by definition so does the msg above it
            above = Message_forum.objects.get(forum = m.forum, position = m.position+1)
            above.position -= 1
            m.position += 1
            above.save()
            m.save()    
        elif m.position == None:
            # go from where positions end till this message, setting positions
            need_pos = Message_forum.objects.filter(forum = m.forum, status = Message_forum.STATUS_APPROVED, message__lft = 1, position = None, message__date__gt = m.message.date).order_by('-message__date')
            # start with the next position
            min_pos = forum_msgs.aggregate(Min('position'))
            min = min_pos.values()[0]
            above = None
            if min:
                above = forum_msgs.get(position = min)
                pos = min - 1
            else:
                # there are currently no positions
                pos = count
            for msg in need_pos:
                msg.position = pos
                pos -= 1
                msg.save()
                above = msg
            
            # swap positions with the last msg
            # use above so that we avoid setting position
            # for top-most msg if not already set
            if above:
                m.position = above.position
                above.position -= 1
                m.save()
                above.save()
            
    elif direction == 'down':
        if m.position and m.position > 1:
            # get the message below
            min_pos = forum_msgs.aggregate(Min('position'))
            min = min_pos.values()[0]
            if min == m.position:
                # below is the first msg without a position
                # it should always exist since position accomodates all msgs in forum
                below = Message_forum.objects.filter(forum = m.forum, status = Message_forum.STATUS_APPROVED, message__lft=1, position = None).order_by('-message__date')[:1]
                below = below[0]
            else:
                below = Message_forum.objects.get(forum = m.forum, position = m.position-1)
            
            # swap positions
            below.position = m.position
            m.position -= 1
            below.save()
            m.save()
            
        elif m.position == None:
            # get below message
            # do the check first to avoid any work if this is the last msg
            below = Message_forum.objects.filter(forum = m.forum, status = Message_forum.STATUS_APPROVED, message__lft=1, message__date__lt = m.message.date).order_by('-message__date')[:1]
            if below.count() == 1:
                below = below[0]
                
                # go from where positions end till this message, setting positions
                need_pos = Message_forum.objects.filter(forum = m.forum, status = Message_forum.STATUS_APPROVED, message__lft = 1, position = None, message__date__gt = m.message.date).order_by('-message__date')
                # start with the next position
                min_pos = forum_msgs.aggregate(Min('position'))
                min = min_pos.values()[0]
                if min:
                    pos = min - 1
                else:
                    # there are currently no positions
                    pos = count
                for msg in need_pos:
                    msg.position = pos
                    pos -= 1
                    msg.save()
                
                # pos is now set for the msg to be swapped
                below.position = pos
                m.position = pos - 1
                below.save()
                m.save()
            
    return HttpResponseRedirect(reverse('otalo.ao.views.messageforum', args=(m.id,)))
    

@csrf_exempt    
def record_or_upload_message(request):
    params = request.POST
    if 'main' in request.FILES:
        main = request.FILES['main']
        extension = main.name[main.name.index('.'):]
        
        if params['options'] == 'upload':
            #validating file type, it should be mp3 or wav only
            if extension != '.mp3' and extension != '.wav':
                response = HttpResponse('[{"model":"VALIDATION_ERROR", "type":'+INVALID_FILE_FORMAT+', "message":"mp3 format required"}]')
                response['Pragma'] = "no cache"
                response['Cache-Control'] = "no-cache, must-revalidate"
                return response
            
        date=None
        if 'when' in params:
            when = params['when']
            if when == 'date':
                bcastdate = params['date']
                try:
                    date = datetime.strptime(bcastdate, '%b-%d-%Y')
                except ValueError as err:
                    response = HttpResponse('[{"model":"VALIDATION_ERROR", "type":'+INVALID_DATE+', "message":"invalid date"}]')
                    response['Pragma'] = "no cache"
                    response['Cache-Control'] = "no-cache, must-revalidate"
                    return response
                    
                hour = int(params['hour'])
                min = int(params['min'])
                date = datetime(year=date.year,month=date.month,day=date.day,hour=hour,minute=min)
       
        if 'number' in params:
            number = params['number'].strip()
            author = User.objects.filter(number=number)
            if author:
                author = author[0]
            else:
                # try to get a 10-digit number
                number = get_phone_number(number)
                if number:
                    author = User(number=number, allowed='y')
                    author.save()
                else:
                    response = HttpResponse('[{"model":"VALIDATION_ERROR", "type":'+INVALID_NUMBER+', "message":"invalid number"}]')
                    response['Pragma'] = "no cache"
                    response['Cache-Control'] = "no-cache, must-revalidate"
                    return response
        else:
            auth_user = request.user
            author = User.objects.filter(admin__auth_user=auth_user).distinct()[0]
            number = author.number
        
        parent = False
        if params['messageforumid']:
            parent = get_object_or_404(Message_forum, pk=params['messageforumid'])
            f = parent.forum
        else:
            f = get_object_or_404(Forum, pk=params['forumid'])
            
        mf = createmessage(f, main, author, parent, date)
        
        '''
        syncing message file to all the machines, getting machine id's from dialers associated with the selected group's line 
        '''
        sync_utils.sync_file((mf.message.file.path), mf.forum.line_set.all()[0].dialers.all())
        
        # do this after createmessage so that an answer call will use the wav file
        # which was just saved above
        if parent and mf.status == Message_forum.STATUS_APPROVED and mf.forum.response_calls:
            broadcast.answer_call(f.line_set.all()[0], mf)
            
        return HttpResponseRedirect(reverse('otalo.ao.views.messageforum', args=(mf.id,)))
    else:
        response = HttpResponse('[{"model":"VALIDATION_ERROR", "type":'+NO_CONTENT+',"message":"content required"}]')
        response['Pragma'] = "no cache"
        response['Cache-Control'] = "no-cache, must-revalidate"
        return response


'''
'    If the given file is mp3; create a wav (to play over IVR)
'    If the given file is wav; create a mp3 (to play over web) and make wav suitable for IVR
'''
def create_wav_mp3_companion(file_path):
    #converting audio file from one to another
    #getting to path, at this path file could be mp3 or wav
    if ".wav" in file_path:
        to_path = file_path[0:file_path.rfind(".wav")] + ".mp3"
        command = "ffmpeg -y -i %s"%(file_path) + " -f mp3 -ac 1 %s"%(to_path)
        subprocess.call(command, shell=True)
        
        #now resampling file to 8k mono
        file_path_converted = file_path[0:file_path.index('.')] + "_tmp.wav"
        command = "ffmpeg -y -i %s"%(file_path) + " -f wav -acodec pcm_mulaw -ar 8000 -ac 1 %s"%(file_path_converted)
        subprocess.call(command, shell=True)
        #renaming file to original wav
        os.rename(file_path_converted, file_path)
        
    else:
        to_path = file_path[0:file_path.rfind(".mp3")] + ".wav"
        command = "ffmpeg -y -i %s"%(file_path) + " -f wav -acodec pcm_mulaw -ar 8000 -ac 1 %s"%(to_path)
        subprocess.call(command, shell=True)

def createmessage(forum, content, author, parent=None, date=None):
    content.name = generate_filename(content)
    pos = None
    msg = Message.objects.create(date=date or datetime.now(), file=content, user=author)
    
    if bool(Admin.objects.filter(user=author,forum=forum)):
        status = Message_forum.STATUS_APPROVED
        if not parent:
            # only set position if there are some already set
            msgs = Message_forum.objects.filter(forum=forum, status=Message_forum.STATUS_APPROVED, message__lft = 1).order_by('-position')
            if msgs.count() > 0 and msgs[0].position != None:
                pos = msgs[0].position + 1
    else:
        status = Message_forum.STATUS_PENDING
    msg_forum = Message_forum.objects.create(message=msg, forum=forum,  status=status, position = pos)
    if parent:
        add_child(msg, parent.message)
        
    #converting file from mp3 to wav or from wav to mp3
    create_wav_mp3_companion(msg_forum.message.file.path)
    if '.wav' not in msg_forum.message.file.name:
        relative_path = msg_forum.message.file.name
        #updating message object with wav file
        wav_file_path = relative_path[:relative_path.rfind('.')] + '.wav'
        msg_forum.message.file = wav_file_path
        msg_forum.message.save()
    return msg_forum

def generate_filename(f):
    t = datetime.now()
    extension = f.name[f.name.index('.'):]
    return t.strftime("%m-%d-%Y_%H%M%S") + str(t.microsecond)[-3] + extension
    
def thread(request, message_forum_id):
    m = get_object_or_404(Message_forum, pk=message_forum_id)
    msg = m.message
    if msg.lft == 1: # this is the parent thread
        top = msg
    else:
        top = msg.thread
    thread_msg_forums = (Message_forum.objects.filter(message__thread=top) | Message_forum.objects.filter(message=top)).order_by('message__lft')
    return send_response (thread_msg_forums, {'message':{'relations':{'user':{'fields':('name', 'number',)}}}, 'forum':{'fields':('pk')}})

@csrf_exempt
def updatestatus(request, action):
    params = request.POST 

    m = get_object_or_404(Message_forum, pk=params['messageforumid'])
    current_status = m.status
    
    if action == 'approve' and current_status != Message_forum.STATUS_APPROVED:
        m.status = Message_forum.STATUS_APPROVED
        
        if m.message.lft == 1:
            # only set position if there are some already set
            msgs = Message_forum.objects.filter(forum=m.forum, status=Message_forum.STATUS_APPROVED, message__lft = 1).order_by('-position')
            if msgs.count() > 0 and msgs[0].position != None:
                m.position = msgs[0].position + 1
        else:
            '''
            '    Deliberately not checking if response call has already been created
            '    (not Prompt.objects.filter(file__contains=m.message.file.name)
            '    to allow moderator to re-send response call by rejecting and re-approving msg
            '''
            if m.forum.response_calls:
                broadcast.answer_call(m.forum.line_set.all()[0], m)
            
            
    elif action == 'reject' and current_status != Message_forum.STATUS_REJECTED: # newly rejecting
        m.status = Message_forum.STATUS_REJECTED
        # Reject all responses
        if m.message.lft == 1:
            top = m.message
        else:
            top = m.message.thread
        responses = Message_forum.objects.filter(forum = m.forum, message__thread=top, message__lft__gt=m.message.lft, message__rgt__lt=m.message.rgt)
        for msg in responses:
            msg.status = Message_forum.STATUS_REJECTED
            msg.save()
        
        if m.message.lft == 1 and m.position:
            # bump down the position of everyone ahead
            ahead = Message_forum.objects.filter(forum = m.forum, status = Message_forum.STATUS_APPROVED, message__lft=1, position__gt=m.position)
            for msg in ahead:
                msg.position -= 1
                msg.save()

            m.position = None

    m.save()
    
    return HttpResponseRedirect(reverse('otalo.ao.views.messageforum', args=(int(m.id),)))

def tags(request, forum_id=None):
    
    if forum_id is None:
        fora = get_forums(request)
        tags = Tag.objects.filter(forum__in=fora).order_by('tag').distinct()   
    else:
        params = request.GET
        
        forum = get_object_or_404(Forum, pk=forum_id)
        tags = Tag.objects.filter(forum=forum).order_by('tag').distinct()
        
        if params.__contains__('type'):
            types = params['type'].split()
            tags = tags.filter(type__in=types)
           
    return send_response(tags)

def tagsbyline(request, line_id):
    params = request.GET
    
    line = get_object_or_404(Line, pk=line_id)
    tags = Tag.objects.filter(forum__line=line).distinct()
    
    if params.__contains__('type'):
        types = params['type'].split()
        tags.filter(type__in=types)
       
    return send_response(tags)

def messagetag(request, message_forum_id):
    tags = Tag.objects.filter(message_forum=message_forum_id)
    return send_response(tags, ('tag'))

def responders(request, forum_id):
    forum = get_object_or_404(Forum, pk=forum_id)
    responders = forum.responders.all()
    return send_response(responders, ('user'))

def messageresponder(request, message_forum_id):
    # TODO: should this list be updated based on passed and reserved settings?
    responders = Message_responder.objects.filter(message_forum=message_forum_id)
    return send_response(responders, ('user'))

def moderator(request):
    auth_user = request.user
    if not auth_user.is_superuser:
        moderator = User.objects.filter(admin__auth_user=auth_user).distinct()
    else:
        moderator = []
    
    return send_response(moderator)

def line(request):
    auth_user = request.user
    
    if not auth_user.is_superuser:
        # get all lines associated with this login
        line = Line.objects.filter(forums__admin__auth_user=auth_user).exclude(forums__status=Forum.STATUS_INACTIVE).distinct().order_by('-id')
    else:
        line = Line.objects.filter(pk=1)
        
    return send_response(line)

def survey(request):
    params = request.GET
    auth_user = request.user
    start = int(params['start'])
    
    surveys = Survey.objects.filter(broadcast=True).exclude(name__contains=Survey.ANSWER_CALL_DESIGNATOR).order_by('-id')
    if not auth_user.is_superuser:
        # get all lines associated with this login
        # change to auth_user.id from auth_user to account for SimpleLazyObject error: 
        lines = Line.objects.filter(forums__admin__auth_user=auth_user.id).distinct()
        numbers = []
        for line in lines:
            numbers.append(line.number)
            if line.outbound_number:
                numbers.append(line.outbound_number)
        
        surveys = surveys.filter(number__in=numbers, created_on__gt=auth_user.date_joined)
    
    surveys = surveys[start:start+BCAST_PAGE_SIZE]
    for survey in surveys:
        # update the status
        survey.getstatus()
        
    return send_response(surveys)

@csrf_exempt
def bcast(request):
    params = request.POST
    surveyid = params['survey']
    template = get_object_or_404(Survey, pk=surveyid)
    if params['messageforumid']:
        message_forum_id = int(params['messageforumid'])
        mf = get_object_or_404(Message_forum, pk=message_forum_id)
        line = mf.forum.line_set.all()[0]
    else:
        mf = None
        # can't trust line ID in case of an account with multiple lines (like a survey account)
        # in that case the best place to get the line is from the template's number
        # order by -id in case we forget to deactivate the forums of an older line
        # NOTE: excluding by Inactive forum status will filter out Lines with *at least* one inactive forum (not all inactive forums)
        line = Line.objects.filter(number=template.number).exclude(forums__status=Forum.STATUS_INACTIVE).order_by('-id')[0]
    
    subjects = []
    # Get subjects
    if params.__contains__('bynumbers'):
        numsRaw = params['numbersarea']
        if ',' in numsRaw:
            numbers = numsRaw.split(',')
        elif '\n' in numsRaw:
            numbers = numsRaw.split('\n')
        else:
            numbers = [numsRaw]
        
        subjects += broadcast.subjects_by_numbers(numbers)  
    
    if params.__contains__('bytag'):
        tagids = params.getlist('tag')
        tags = Tag.objects.filter(pk__in=tagids)
        subjects += broadcast.subjects_by_tags(tags, line)
    
    
    '''
    This is dormant until we are able to track all inbound calls by db. We can no
    longer rely on logs on local servers because our dialing system is distributed
    
    if params.__contains__('bylog'):
        lastncallers = params['lastncallers']
        since = params['since']
        
        if lastncallers == 'ALL':
            lastncallers = 0
        else:
            lastncallers = int(lastncallers)
        
        if since:
            since = datetime.strptime(since, '%b-%d-%Y')
        else:
            # in case no date is selected, get no subjects
            since = datetime.now()
               
        subjects += broadcast.subjects_by_log(line, since, lastncallers)
    '''
    
    # remove dups
    subjects = list(set(subjects))
    
    # Get name
    bcastname = params['bcastname']
    
    num_backups = int(params["backup_calls"])
    
    # Get schedule
    when = params['when']
    if when == 'now':
        start_date = datetime.now()
    elif when == 'date':
        start_date = params['date']
        try:
            start_date = datetime.strptime(start_date, '%b-%d-%Y')
        except ValueError as err:
            response = HttpResponse('[{"model":"VALIDATION_ERROR", "type":'+INVALID_DATE+', "message":"invalid date"}]')
            response['Pragma'] = "no cache"
            response['Cache-Control'] = "no-cache, must-revalidate"
            return response
        
        hour = int(params['hour'])
        min = int(params['min'])
        start_date = datetime(year=start_date.year,month=start_date.month,day=start_date.day,hour=hour,minute=min)

    if mf is not None:
        responseprompt = params.__contains__('response')
        # make synchronous in order to update the bcasts view immediately
        broadcast.thread(mf, template, subjects, responseprompt, num_backups, start_date, bcastname)
    else:
        # make synchronous in order to update the bcasts view immediately
        broadcast.regular_bcast(line, template, subjects, num_backups, start_date, bcastname)
    
    if params['messageforumid']:
        return HttpResponseRedirect(reverse('otalo.ao.views.messageforum', args=(int(params['messageforumid']),)))
    else:
        return HttpResponseRedirect(reverse('otalo.ao.views.forum'))

def forwardthread(request, message_forum_id):
    mf = get_object_or_404(Message_forum, pk=message_forum_id)
    
    # check if this forum has a designated template
    template = mf.forum.bcast_template
    
    if template:
        templates = [template]
    else:
        lines = mf.forum.line_set.all()
        numbers = []
        for line in lines:
            if line.number not in numbers:
                numbers.append(line.number)
            if line.outbound_number and line.outbound_number not in numbers:
                numbers.append(line.outbound_number)
                
        templates = Survey.objects.filter(template=True, number__in=numbers)
    
    return send_response(templates)

def regularbcast(request):
    auth_user = request.user
    
    templates = Survey.objects.filter(template=True)
    if not auth_user.is_superuser:
        # get all lines associated with this login
        # change to auth_user.id from auth_user to account for SimpleLazyObject error:
        lines = Line.objects.filter(forums__admin__auth_user=auth_user.id).exclude(forums__status=Forum.STATUS_INACTIVE).distinct()
        numbers = []
        for line in lines:
            numbers.append(line.number)
            if line.outbound_number:
                numbers.append(line.outbound_number)
        
        templates = templates.filter(number__in=numbers)
        
    return send_response(templates)

def surveyinput(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    
    # get all prompts in reverse order so that the last ones will be inserted first into the widget
    prompts = Prompt.objects.filter(survey=survey, option__action=Option.RECORD).distinct().order_by('-order')
    
    return send_response(prompts, relations=('survey',))

def cancelsurvey(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    survey.status = Survey.STATUS_CANCELLED
    survey.save()
        
    return send_response([survey])

def surveydetails(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    
    calls = Call.objects.filter(survey=survey)
    
    firstcalldate = 'Not Started (scheduled for '+str(survey.created_on)+ ')' if survey.created_on else 'Not Started'
    if calls:
        firstcalldate = calls.aggregate(Min('date'))
        firstcalldate = firstcalldate.values()[0]
    
    if survey.subjects.all():
        numbers = survey.subjects.all()
        numbers = [su.number for su in numbers]
    else:
        numpairs = calls.values('subject__number').distinct()
        numbers = [pair.values()[0] for pair in numpairs]
    
    numpairscomplete = calls.filter(complete=True).values('subject__number').distinct()
    completed_numbers = [pair.values()[0] for pair in numpairscomplete]
    pending_numbers = list(set(numbers) - set(completed_numbers))
    completed = ', '.join(completed_numbers)
    pending = ', '.join(pending_numbers)
    
    response = HttpResponse('[{"model":"SURVEY_METADATA", "startdate":"'+str(firstcalldate)+'","completed":"'+completed+'","pending":"'+pending+'"}]')
    response['Pragma'] = "no cache"
    response['Cache-Control'] = "no-cache, must-revalidate"
    return response
      
def promptresponses(request, prompt_id):
    params = request.GET
    
    prompt = get_object_or_404(Prompt, pk=prompt_id)
    start = int(params['start'])
    input = Input.objects.filter(prompt=prompt)
    count = input.count()
    input = input[start:start+VISIBLE_MESSAGE_COUNT]
    
    resp = send_response(input, relations={'call':{'relations':{'subject':{'fields':('name','number',)}}}, 'prompt':()} )
    
    if count > 0:
        # append some meta info about the messages
        # remove end bracket
        jsonresp = resp.content[:-1]
        jsonresp += ', {"model":"MESSAGE_METADATA", "start":'+str(start)+', "count":'+str(count)+'}]'
        resp.content = jsonresp
    
    return resp
    
def get_console_user(request):
   auth_user = request.user
   u = User.objects.filter(admin__auth_user=auth_user).distinct()
   u = u[0]
   return u;

# make child the last of this parent
def add_child(child, parent):
    if parent.lft == 1: # top-level thread
        child.thread = parent
    else:
        child.thread = parent.thread

    child.lft = parent.rgt
    child.rgt = child.lft + 1
    child.save()

    # update all nodes to the right of the child
    # use child.lft to include the immediate parent (the algorithm typically asks you to get all nodes
    # to the rgt of the current parent's rgt, which is child.lft)
    msgs = Message.objects.filter(Q(thread=child.thread, rgt__gte=child.lft) | Q(pk=child.thread.id)).exclude(pk=child.id)

    for m in msgs:
        m.rgt += 2
        if (m.lft >= child.lft):
            m.lft += 2
        m.save()
        

def download(request, model, model_id):
    if model == 'mf':
        mf = get_object_or_404(Message_forum, pk=model_id)
        fname = mf.message.file.path
    elif model == 'si':
        input = get_object_or_404(Input, pk=model_id)
        fname = settings.MEDIA_ROOT + '/' + input.input
    
    return send_file(fname,'application/octet-stream')

def sms(request, line_id):
    params = request.GET
    start = int(params['start'])
    type = int(params['type'])
    
    line = get_object_or_404(Line, pk=int(line_id))
    line_user = User.objects.filter(number=line.number)
    console_user = get_console_user(request)
    
    if type == SMSListType_SENT:  
        msgs = SMSMessage.objects.filter(sender__in=[line_user[0] if line_user else None, console_user]).order_by('-id')
    elif type == SMSListType_IN:
        msgs = SMSMessage.objects.filter(recipients__number__in=[line.number]).order_by('-id')
    
    count = msgs.count()      
   
    # fell off the page
    if start >= count and start > 0:
        start -= VISIBLE_MESSAGE_COUNT
    msgs = msgs[start:min(count,start+VISIBLE_MESSAGE_COUNT)]
        
    resp = send_response(msgs, relations=('sender',))
    
    if count > 0:
        # append some meta info about the messages
        # remove end bracket
        jsonresp = resp.content[:-1]
        jsonresp += ', {"model":"MESSAGE_METADATA", "start":'+str(start)+', "count":'+str(count)+', "type":'+str(type)+'}]'
        resp.content = jsonresp
        
    return resp

def smsrecipients(request, smsmsg_id):
    msg = get_object_or_404(SMSMessage, pk=smsmsg_id)
    recipients = msg.recipients.all()
    
    return send_response(recipients)

@csrf_exempt
def sendsms(request):
    params = request.POST
    line = get_object_or_404(Line, pk=int(params['lineid']))
    
    recipients = []
    # Get recipients
    if params.__contains__('bynumbers'):
        numsRaw = params['numbersarea']
        if ',' in numsRaw:
            numbers = numsRaw.split(',')
        elif '\n' in numsRaw:
            numbers = numsRaw.split('\n')
        else:
            numbers = [numsRaw]
        
        for number in numbers:
            number = number.strip()
            number = number[-10:]
            if number == '':
                continue
            u = User.objects.filter(number=number)
            if bool(u):
                if u[0].allowed == 'n':
                    continue
                else:
                    u = u[0]
            else:
                u = User(number=number,allowed='y')
                u.save()
            recipients.append(u)  
    
    if params.__contains__('bytag'):
        tagids = params.getlist('tag')
        tags = Tag.objects.filter(pk__in=tagids)
        users = User.objects.filter(Q(message__message_forum__tags__in=tags, message__message_forum__forum__line=line) | Q(tags__in=tags)).distinct()
        users = users.filter(allowed='y', indirect_bcasts_allowed=True)
        
        for u in users:
            recipients.append(u)
    
    if params.__contains__('bylog'):
        lastncallers = params['lastncallers']
        since = params['since']
        
        if lastncallers == 'ALL':
            lastncallers = 0
        else:
            lastncallers = int(lastncallers)
        
        if since:
            since = datetime.strptime(since, '%b-%d-%Y')
        else:
            # in case no date is selected, get no recipients
            since = datetime.now()
               
        filename = settings.INBOUND_LOG_ROOT+str(line.id)+'.log'
        calls = stats_by_phone_num.get_numbers_by_date(filename=filename, destnum=str(line.number), date_start=since, quiet=True)
        numbers = calls.keys()
        
        if lastn:
            numbers = numbers[:lastn]
            
        for number in numbers:
            u = User.objects.filter(number=number, allowed='y', indirect_bcasts_allowed=True)
            if bool(u):
                u = u[0]
            else:
                u = User(number=number,allowed='y')
                u.save()
            recipients.append(u) 
    
    if params.__contains__('group'):
        group = params['group']
        # if not selected, group will be an invalid ID
        users = User.objects.filter(membership__status=Membership.STATUS_SUBSCRIBED, membership__group=group)
        
        for u in users:
            recipients.append(u)
        
    # remove dups
    recipients = list(set(recipients))
    
    if len(recipients) == 0:
        response = HttpResponse('[{"model":"VALIDATION_ERROR", "type":'+NO_CONTENT+', "message":"No recipients specified"}]')
        response['Pragma'] = "no cache"
        response['Cache-Control'] = "no-cache, must-revalidate"
        return response
    
    # Get msg
    smstext = params['txt']
    smstext = smstext.encode('ascii', 'ignore')
    if smstext == '':
        response = HttpResponse('[{"model":"VALIDATION_ERROR", "type":'+NO_CONTENT+', "message":"Please enter some text"}]')
        response['Pragma'] = "no cache"
        response['Cache-Control'] = "no-cache, must-revalidate"
        return response
    
    # charge the customer if this is a paying customer
    sender = get_console_user(request)
    # check balance in backend in case UI check fails to capture negative balance
    # (i.e. if user hasn't refreshed his screen in a while and UI doesn't update in real time)
    if recipients:
        if sender.balance is not None: 
            if sender.balance == Decimal(str(User.UNLIMITED_BALANCE)) or sender.balance > Decimal(str(sms_utils.SMS_DISALLOW_BALANCE_THRESH)):
                numsms = math.ceil(len(smstext) / float(SMS_LENGTH))
                sms_utils.charge_sms_credits(sender, len(recipients) * numsms)
                sms_utils.send_sms(line.sms_config, recipients, smstext, sender)
            else:
                response = HttpResponse('[{"model":"VALIDATION_ERROR", "type":'+NOT_ENOUGH_BALANCE+', "message":"Insufficient balance to send SMS"}]')
                response['Pragma'] = "no cache"
                response['Cache-Control'] = "no-cache, must-revalidate"
                return response
        else:
            sms_utils.send_sms_from_line(line, recipients, smstext)
    
    return HttpResponseRedirect(reverse('otalo.ao.views.forum'))

def smsin(request):
    params = request.GET
    '''
    The below post params are hardcoded, since you need to get the keyword
    and dest in order to get the right config. For your own inbound SMS,
    you will have to alter or create seperate
    post locations for different service providers
    '''
    sender = params['msisdn'][-10:]
    message = params['message']
    dest = params['shortcode'][-10:]
    
    # get the keyword
    keyword = message.split(' ')[0]
    
    line = Line.objects.filter(sms_config__keyword=keyword, sms_config__inbound_number=dest)
    if bool(line):
        line = line[0]
        dest = User.objects.get(number=line.number)
        u = User.objects.filter(number=sender)
        if bool(u):
            u = u[0]
        else:
            u = User(number=sender, allowed='y')
            u.save()
        msg = SMSMessage(sender=u, text=message)
        msg.save()
        msg.recipients.add(dest)
    
    return send_data('ok') 

def get_phone_number(number, ten_digits_only=True):
    # strip non-numerics and see if we have
    # a ten-digit number left.
    # Not full-proof, but accomodates all standard
    # number entry styles
    number = str(number) if isinstance(number, (int, long)) else number
    number = number.encode('ascii', 'ignore').strip()
    if number is None:
        return number
    number = re.sub(r'[^\d]+','',str(number))
    if len(number) >= 10:
        return number[-10:] if ten_digits_only else number
    # if less than ten chars, see if it's a number
    # and we are allowing numbers that aren't ten digits
    elif number.isdigit() and not ten_digits_only:
        return number
    else:
        return None
    
def send_file(filename, content_type):
    """                                                                         
    Send a file through Django without loading the whole file into              
    memory at once. The FileWrapper will turn the file object into an           
    iterator for chunks of 8KB.                                                 
    """                            
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type=content_type)
    response['Content-Length'] = os.path.getsize(filename)
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    return response

# Expects data to be in JSON format i.e. {a:b, c:{d:e}}
def send_data(json_data):
    response = HttpResponse(json_data)
    response['Pragma'] = "no cache"
    response['Cache-Control'] = "no-cache, must-revalidate"
    return response;

def send_response(query_set, relations=(), excludes=()):
    json_serializer = serializers.get_serializer("json")()
    response = HttpResponse(json_serializer.serialize(query_set, relations=relations, excludes=excludes))
    response['Pragma'] = "no cache"
    response['Cache-Control'] = "no-cache, must-revalidate"
    return response;


def combined_resultsets(resultset1, resultset2, sortby):
    if sortby is not None:
        resultset1 = sorted(chain(resultset1, resultset2),key=attrgetter(sortby))
    else:
        resultset1 = chain(resultset1, resultset2)
    

def get_forums(request):
    #getting users's forum first
    auth_user = request.user
    if not auth_user.is_superuser:
        # get all forums that this user has access to
        fora = Forum.objects.filter(admin__auth_user=auth_user).exclude(status=Forum.STATUS_INACTIVE).distinct()
    else:
        fora = Forum.objects.all()
    
    return fora

@csrf_exempt
def search(request):
    params = request.POST
    search_data = json.loads(params[SEARCH_PARAM])
    
    forums = []
    if SEARCH_PARAM_FORUM in search_data and search_data[SEARCH_PARAM_FORUM] != '':
        forums.append(search_data[SEARCH_PARAM_FORUM])
    else:
        fora = get_forums(request)
        for forum in fora:
            forums.append(forum.id)
        
    filts = []
    message_forums = []
    
    
    results = SearchQuerySet().filter(SQ(forum_id__in=forums))    
    count = results.count()
        
    page = search_data[PAGE_PARAM]
        
    if count > 0:
        #if search keyword is present then checking it against the message author fields
        search_keyword = search_data[SEARCH_KEYWORD]
            
        if search_keyword is not None and len(search_keyword) > 0:
            if search_data[AUTHOR] is not None and len(search_data[AUTHOR]) > 0:
                selected_author_fields = search_data[AUTHOR].split(",")
                    
                author_cond = SQ()
                    
                if AUTHOR_NAME in selected_author_fields:
                    #results = results.autocomplete(author_name=search_keyword)
                    author_cond |= SQ(author_name__contains=search_keyword)
     
                if AUTHOR_NUMBER in selected_author_fields:
                    author_cond |= SQ(author_number__contains=search_keyword)
                    
                if AUTHOR_DISTRICT in selected_author_fields :
                    author_cond |= SQ(author_district__contains=search_keyword)
                    
                if AUTHOR_TALUKA in selected_author_fields:
                    author_cond |= SQ(author_taluka__contains=search_keyword)
                    
                if AUTHOR_VILLAGE in selected_author_fields:
                    author_cond |= SQ(author_taluka__contains=search_keyword)
                        
                results = results.filter(author_cond)
                         
            elif len(search_keyword) > 0:
                results = results.autocomplete(text=search_keyword)
                #results = results.filter(content=search_keyword)
                
        # if status is passed then appending it into filter criteria
        if search_data[STATUS] is not None and len(search_data[STATUS]) > 0:
            selected_status = search_data[STATUS].split(",")
                
            if len(selected_status) > 0:
                status_cond = SQ()
                if STATUS_RESPONDED in selected_status:
                    del selected_status[selected_status.index(STATUS_RESPONDED)]
                    #now appending filter for responded message
                    status_cond |= SQ(message_thread_id__gt=-1)
                    
                #appending other status filters
                if len(selected_status) > 0:    
                    status_cond |= SQ(status__in=selected_status)
                filts.append(status_cond)
            
        # if tags are passed then appending them into filter criteria
        if search_data[TAG] is not None and len(search_data[TAG]) > 0:
            selected_tags = search_data[TAG].split(TAG_SEPERATOR)
                
            if len(selected_tags) > 0:
                for tag in selected_tags:
                    filts.append(SQ(tags__conatains=tag))
                
            
        # if from date is passed then appending it into filter criteria
        # from server side date would be always comes in format of yyyy-MM-dd only. 
        #If need to be change then change it on the both the place. i.e. client and server
        # e.g. 2013-09-17
            
        date_format = '%Y-%m-%d'
        if search_data[FROMDATE] is not None and len(search_data[FROMDATE]) > 0:
            from_date = datetime.strptime(search_data[FROMDATE], date_format)
            filts.append(SQ(message_date__gte=from_date))
        
        # if to date is passed then appending it into filter criteria
        if search_data[TODATE] is not None and len(search_data[TODATE]) > 0:
            to_date = datetime.strptime(search_data[TODATE], date_format)
            filts.append(SQ(message_date__lte=to_date))
            
            
        for filt in filts:
            results = results.filter(filt)
            
        results = results.order_by('-message_date')
        count = results.count()
    
    #implementing the pagination code here
    paginator = Paginator(results, VISIBLE_MESSAGE_COUNT) # Show VISIBLE_MESSAGE_COUNT messages per page
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(page)
    except ValueError:
        page = 1
    
    # If page request (9999) is out of range, deliver last page of results.
    try:
        messages = paginator.page(page)
    except (EmptyPage, InvalidPage):
        messages = paginator.page(paginator.num_pages)
    
    messageobjs = [r.object for r in messages]
    resp = send_response(messageobjs, {'message':{'relations':{'user':{'fields':('name', 'number',)}}}, 'forum':{'fields':('name', 'moderated', 'responses_allowed', 'posting_allowed', 'routeable')}})
    
    if count > 0:
        # append some meta info about the messages
        # remove end bracket
        jsons = resp.content[:-1]
        jsons += ', {"model":"MESSAGE_METADATA"'
        if messages.has_next():
            jsons += ', "previous_page":'+str(messages.next_page_number())
        if messages.has_previous():
            jsons += ', "next_page":'+str(messages.previous_page_number())
        
        jsons += ', "current_page":'+str(page)
        jsons+= ', "count":'+str(count)+'}]'
        resp.content = jsons
    return resp