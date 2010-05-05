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

from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from otalo.AO.models import Forum, Message, Message_forum, User, Tag, Message_tag, Responder_tag, Message_responder
from django.core import serializers
from django.conf import settings
from django.db.models import Min, Count
from datetime import datetime
import os, stat

# Code in order of how they are declared in Message.java
MESSAGE_STATUS_PENDING = 0
MESSAGE_STATUS_APPROVED = 1
MESSAGE_STATUS_REJECTED = 2

# Routing Constants
MAX_RESPONDERS = 5
MIN_RESPONDERS = 2
MAX_QUESTIONS_PER_RESPONDER = 10
# should match answer.lua
LISTEN_THRESH = 5

@login_required
def index(request):
    #return render_to_response('AO/index.html', {'fora':fora})
    return render_to_response('Ao.html')

def forum(request):
    #f = get_object_or_404(Forum,pk=forum_id)
    #return render_to_response('AO/forum/index.html', {'forum':f})

    fora = Forum.objects.all()
    return send_response(fora)

def messages(request, forum_id):
    params = request.GET
    
    status = params['status'].split()
    posttype = params['posttype']
    
    if posttype == 'top':
        message_forums = Message_forum.objects.filter(forum=forum_id, status__in=status, message__lft=1).order_by('-position', '-message__date')
    elif posttype == 'responses':
        message_forums = Message_forum.objects.filter(forum=forum_id, status__in=status, message__lft__gt=1).order_by('-position', '-message__date')
    elif posttype == 'all':
        message_forums = Message_forum.objects.filter(forum=forum_id, status__in=status).order_by('-position', '-message__date')
       
    return send_response(message_forums, {'message':{'relations':{'user':{'fields':('name', 'number',)}}}, 'forum':{'fields':()}})

def messageforum(request, message_forum_id):
    # Note use of filter instead of get to return a query set
    message = get_list_or_404(Message_forum, pk=message_forum_id)
    # means don't put any restrictions on the fields returned for forum relation
    return send_response(message, {'message':{'fields':()}, 'forum':{}})

def user(request, user_id):
    # Note use of filter instead of get to return a query set
    user = get_list_or_404(User, pk=user_id)
    return send_response(user)

def updatemessage(request):
    params = request.POST
    
    u = User.objects.get(pk=params['userid'])
    u.number = params['number']
    u.name = params['name']
    u.district = params['district']
    u.taluka = params['taluka']
    u.village = params['village']

    u.save()   

    m = get_object_or_404(Message_forum, pk=params['messageforumid'])

    if not params.__contains__('position'):
        m.position = None
        m.save()

    # Check to see if there was a response uploaded
    if request.FILES:
        f = request.FILES['response']
        resp = createmessage(m.forum, f, parent=m)
        
    # Save tags
    crop = params['crop']
    topic = params['topic']
    
    tags = Message_tag.objects.filter(message_forum = m)
    initial_tag = False
    if not tags and (crop != '-1' or topic != '-1'):
        # if there aren't any previous tags
        # and there is at least one new one
        # (even if you can untag completely, we still want this flag set)
        initial_tag = True
    else:   
        tags.delete()
    
    if crop != '-1':
        crop_tag = Tag.objects.get(pk=crop)
        new_crop_tag = Message_tag(message_forum = m, tag=crop_tag)
        new_crop_tag.save()
    
    if topic != '-1':
        topic_tag = Tag.objects.get(pk=topic)
        new_topic_tag = Message_tag(message_forum = m, tag=topic_tag)
        new_topic_tag.save()
    
    if m.forum.routeable == 'y':
        # check routing table
        routeEnabled = params.__contains__('routeEnabled')
        if routeEnabled:
            # checked
            
            # do fresh assignments even if it's the same people to start again
            Message_responder.objects.filter(message_forum=m).delete()
            responders = get_responders(m)
            t = datetime.now()
            for responder in responders:
                mr = Message_responder(message_forum=m, user=responder, assign_date=t)
                mr.save();
        else:
            # check if tags are being saved for the first time
            if initial_tag:
                responders = get_responders(m)
                t = datetime.now()
                for responder in responders:
                    mr = Message_responder(message_forum=m, user=responder, assign_date=t)
                    mr.save();
            else:
                # unchecked; delete any responder assignments that exist
                Message_responder.objects.filter(message_forum=m).delete()
    
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse('otalo.AO.views.messageforum', args=(int(m.id),)))

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
            need_pos = Message_forum.objects.filter(forum = m.forum, status = MESSAGE_STATUS_APPROVED, message__lft = 1, position = None, message__date__gt = m.message.date).order_by('-message__date')
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
                below = Message_forum.objects.filter(forum = m.forum, status = MESSAGE_STATUS_APPROVED, message__lft=1, position = None).order_by('-message__date')[:1]
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
            below = Message_forum.objects.filter(forum = m.forum, status = MESSAGE_STATUS_APPROVED, message__lft=1, message__date__lt = m.message.date).order_by('-message__date')[:1]
            if below.count() == 1:
                below = below[0]
                
                # go from where positions end till this message, setting positions
                need_pos = Message_forum.objects.filter(forum = m.forum, status = MESSAGE_STATUS_APPROVED, message__lft = 1, position = None, message__date__gt = m.message.date).order_by('-message__date')
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
            
    return HttpResponseRedirect(reverse('otalo.AO.views.messageforum', args=(m.id,)))
        
def uploadmessage(request):
    if request.FILES:
        main = request.FILES['main']
        summary = False
        if 'summary' in request.FILES:
            summary = request.FILES['summary']

        f = get_object_or_404(Forum, pk=request.POST['forumid'])
        m = createmessage(f, main, summary)

        return HttpResponseRedirect(reverse('otalo.AO.views.messageforum', args=(m.id,)))

def createmessage(forum, content, summary=False, parent=False):
    t = datetime.now()
    summary_filename = ''

    extension = content.name[content.name.index('.'):]
    filename = t.strftime("%m-%d-%Y_%H%M%S") + extension
    filename_abs = settings.MEDIA_ROOT + '/' + filename
    destination = open(filename_abs, 'wb')
    for chunk in content.chunks():
        destination.write(chunk)
    os.chmod(filename_abs, 0644)
    destination.close()

    if summary:
        extension = summary.name[summary.name.index('.'):]
        summary_filename = t.strftime("%m-%d-%Y_%H%M%S") + '_summary' + extension
        summary_filename_abs = settings.MEDIA_ROOT + '/' + summary_filename
        destination = open(summary_filename_abs, 'wb')
        for chunk in summary.chunks():
            destination.write(chunk)
        os.chmod(summary_filename_abs, 0644)
        destination.close()

    # create a new message for this content
    admin = get_console_user()
    pos = None
    if not parent:
        # only set position if there are some already set
        msgs = Message_forum.objects.filter(forum=forum, status=MESSAGE_STATUS_APPROVED, message__lft = 1).order_by('-position')
        if msgs.count() > 0 and msgs[0].position != None:
            pos = msgs[0].position + 1
    
    resp_msg = Message(date=t, content_file=filename, summary_file=summary_filename, user=admin)
    resp_msg.save()
    resp_msg_forum = Message_forum(message=resp_msg, forum=forum,  status=MESSAGE_STATUS_APPROVED, position = pos)

    if parent:
        add_child(resp_msg, parent.message)

    resp_msg_forum.save()

    return resp_msg_forum

def thread(request, message_forum_id):
    m = get_object_or_404(Message_forum, pk=message_forum_id)
    msg = m.message
    if msg.lft == 1: # this is the parent thread
        top = msg
    else:
        top = msg.thread
    thread_msg_forums = (Message_forum.objects.filter(message__thread=top) | Message_forum.objects.filter(message=top)).order_by('message__lft')
    return send_response (thread_msg_forums, {'message':{'relations':{'user':{'fields':('name', 'number',)}}}, 'forum':{'fields':('pk')}})

def updatestatus(request, action):
    params = request.POST 

    m = get_object_or_404(Message_forum, pk=params['messageforumid'])
    current_status = m.status
    
    if action == 'approve' and current_status != MESSAGE_STATUS_APPROVED:
        m.status = MESSAGE_STATUS_APPROVED
        
        if m.message.lft == 1:
            # only set position if there are some already set
            msgs = Message_forum.objects.filter(forum=m.forum, status=MESSAGE_STATUS_APPROVED, message__lft = 1).order_by('-position')
            if msgs.count() > 0 and msgs[0].position != None:
                m.position = msgs[0].position + 1
            
    elif action == 'reject' and current_status != MESSAGE_STATUS_REJECTED: # newly rejecting
        m.status = MESSAGE_STATUS_REJECTED
        # Reject all responses
        if m.message.lft == 1:
            top = m.message
        else:
            top = m.message.thread
        responses = Message_forum.objects.filter(forum = m.forum, message__thread=top, message__lft__gt=m.message.lft, message__rgt__lt=m.message.rgt)
        for msg in responses:
            msg.status = MESSAGE_STATUS_REJECTED
            msg.save()
        
        if m.message.lft == 1 and m.position:
            # bump down the position of everyone ahead
            ahead = Message_forum.objects.filter(forum = m.forum, status = MESSAGE_STATUS_APPROVED, message__lft=1, position__gt=m.position)
            for msg in ahead:
                msg.position -= 1
                msg.save()

            m.position = None
        
        # remove any assignments to answer this question
        Message_responder.objects.filter(message_forum=m).delete()

    m.save()
    
    return HttpResponseRedirect(reverse('otalo.AO.views.messageforum', args=(int(m.id),)))

def tags(request, forum_id):
    params = request.GET
    
    types = params['type'].split()
    tags = Tag.objects.filter(forum=forum_id, type__in=types)
       
    return send_response(tags)

def messagetag(request, message_forum_id):
    tags = Message_tag.objects.filter(message_forum=message_forum_id)
    return send_response(tags, ('tag'))

def messageresponder(request, message_forum_id):
    responders = Message_responder.objects.filter(message_forum=message_forum_id)
    return send_response(responders, ('user'))

def get_responders(message_forum):
    
    tag_ids = Message_tag.objects.filter(message_forum = message_forum).values_list('tag', flat=True)
    
    # Find users who match at least one of the tags for this message, excluding
    # those who have already passed on this message and have listened to it beyond the listen threshold
    # (the excludes for if a question is re-run for responders), and pick the ones with the least pending questions
    responder_ids = User.objects.filter(responder_tag__tag__in = tag_ids).exclude(message_responder__message_forum=message_forum, message_responder__passed_date__isnull=False).exclude(message_responder__listens__gt=LISTEN_THRESH).values("id").annotate(num_assigned=Count('message_responder__message_forum')).filter(num_assigned__lte=MAX_QUESTIONS_PER_RESPONDER).order_by('num_assigned')[:MAX_RESPONDERS]    
    responder_ids = [row['id'] for row in responder_ids]
    
    if len(responder_ids) < MIN_RESPONDERS:
        old = responder_ids
        # If too few, pick the X with the fewest pending questions
        responder_ids = User.objects.exclude(id__in=old).values('id').annotate(num_assigned=Count('message_responder__message_forum')).order_by('num_assigned')[:MAX_RESPONDERS-len(old)]
        responder_ids = [row['id'] for row in responder_ids]
        responder_ids.extend(old)

    return User.objects.filter(id__in=responder_ids) 
  
# this should return the person logged in.
# Stub it for now.
def get_console_user():
    try:
        return User.objects.get(name__contains="ADMIN")
    except User.DoesNotExist:
        # create
        u = User(number='1001', name="ADMIN", admin='y', allowed='y')
        u.save()
    
        return u

# make child the last of this parent
def add_child(child, parent):
    if parent.lft == 1: # top-level thread
        child.thread = parent
    else:
        child.thread = parent.thread

    child.lft = parent.rgt
    child.rgt = child.lft + 1

    # update all nodes to the right of the child
    msgs = Message.objects.filter(rgt__gte=child.lft).exclude(pk=child.id)

    for m in msgs:
        m.rgt += 2
        if (m.lft >= child.lft):
            m.lft += 2
        m.save()
        
    child.save()
def send_response(query_set, relations=()):
    json_serializer = serializers.get_serializer("json")()
    response = HttpResponse(json_serializer.serialize(query_set, relations=relations))
    response['Pragma'] = "no cache"
    response['Cache-Control'] = "no-cache, must-revalidate"
    return response;


