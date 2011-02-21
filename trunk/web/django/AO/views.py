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
import os, stat
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from otalo.AO.models import Line, Forum, Message, Message_forum, User, Tag, Message_responder, Admin
from otalo.surveys.models import Survey, Prompt, Input, Call
from django.core import serializers
from django.conf import settings
from django.db.models import Min, Count
from datetime import datetime, timedelta
from django.core.servers.basehttp import FileWrapper
import alerts

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
# This variable should be consistent with MessageList.java
VISIBLE_MESSAGE_COUNT = 10

@login_required
def index(request):
    #return render_to_response('AO/index.html', {'fora':fora})
    return render_to_response('Ao.html')

def forum(request):
    auth_user = request.user
    
    if not auth_user.is_superuser:
        # get all forums that this user has access to
        fora = Forum.objects.filter(admin__auth_user=auth_user).distinct()
    else:
        fora = Forum.objects.all()
        
    return send_response(fora, excludes=('messages','tags','responders'))

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
        
    resp = send_response(message_forums, {'message':{'relations':{'user':{'fields':('name', 'number',)}}}, 'forum':{'fields':('name', 'moderated', 'responses_allowed', 'posting_allowed', 'routeable')}})
    
    if count > 0:
        # append some meta info about the messages
        # remove end bracket
        json = resp.content[:-1]
        json += ', {"model":"MESSAGE_METADATA", "start":'+str(start)+', "count":'+str(count)+'}]'
        resp.content = json
        
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
        resp = createmessage(request, m.forum, f, parent=m)
        
    # Save tags
    tags_changed = int(params['tags_changed'])
    if tags_changed:
        crop = params['crop']
        topic = params['topic']
        
        m.tags.clear()
    
        if crop != '-1':
            crop_tag = Tag.objects.get(pk=crop)
            m.tags.add(crop_tag)
        
        if topic != '-1':
            topic_tag = Tag.objects.get(pk=topic)
            m.tags.add(topic_tag)
    
    if m.forum.routeable == 'y':
        # Only run routing algorithm if tags have been updated.
        # But don't override manual setting of responders if they
        # were also made
        responders_changed = int(params['responders_changed'])
        if responders_changed or tags_changed:
            if responders_changed:
                responders = []
                if params.__contains__('responders'):
                    responder_ids = params.getlist('responders')
                    for responder_id in responder_ids:
                        responder = User.objects.get(pk=responder_id)
                        responders.append(responder)
            else: #get responders based on new tags
                responders = get_responders(m)
            
            # must do this delete after get_responders so the routing algorithm
            # can take into account previous pass and listen histories
            Message_responder.objects.filter(message_forum=m).delete()
            t = datetime.now()
            for responder in responders:
                mr = Message_responder(message_forum=m, user=responder, assign_date=t)
                mr.save();
                
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
        m = createmessage(request, f, main, summary)

        return HttpResponseRedirect(reverse('otalo.AO.views.messageforum', args=(m.id,)))

def createmessage(request, forum, content, summary=False, parent=False):
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
    admin = get_console_user(request)
    pos = None
    if not parent:
        # only set position if there are some already set
        msgs = Message_forum.objects.filter(forum=forum, status=MESSAGE_STATUS_APPROVED, message__lft = 1).order_by('-position')
        if msgs.count() > 0 and msgs[0].position != None:
            pos = msgs[0].position + 1
    
    msg = Message(date=t, content_file=filename, summary_file=summary_filename, user=admin)
    msg.save()
    msg_forum = Message_forum(message=msg, forum=forum,  status=MESSAGE_STATUS_APPROVED, position = pos)

    if parent:
        add_child(msg, parent.message)
        # if an upload happens, send the reply outbound no
        # matter the status of the message
        alerts.answer_call(forum.line_set.all()[0], parent.message.user.id, msg_forum)
        
    msg_forum.save()

    return msg_forum

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
        else:
            # this is a reply, send an alert to the original poster
            orig_msg = Message.objects.get(pk=m.message.thread.id)
            userid = orig_msg.user.id
            # XXXX TO DO - TO ACTIVATE NOTIFICATION, uncomment 2 following lines
            # from otalo.notification import notification_utils as notut
            # if m.thread and m.thread.message_forum_set.count()>=1:
            #     parent = m.thread.message_forum_set.all()[0]
            #     notut.process_notification(m, parent)
            #alerts.missed_call(m.forum.line_set.all()[0], [userid])
            if not Prompt.objects.filter(file__contains=m.message.content_file):
                alerts.answer_call(m.forum.line_set.all()[0], userid, m)
            
            
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

    m.save()
    
    return HttpResponseRedirect(reverse('otalo.AO.views.messageforum', args=(int(m.id),)))

def tags(request):
    params = request.GET
    
    if params.__contains__('forumid'):
        forum_id = int(params['forumid'])
        tags = Tag.objects.filter(forum=forum_id).distinct()
    elif params.__contains__('lineid'):
        line_id = int(params['lineid'])
        tags = Tag.objects.filter(forum__line=line_id).distinct()
    else:
        tags = Tag.objects.all()
    
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

def username(request):
    auth_user = request.user
    if not auth_user.is_superuser:
        user = get_list_or_404(User, admin__auth_user=auth_user)
    else:
        user = []
    
    return send_response(user)

def line(request):
    auth_user = request.user
    
    if not auth_user.is_superuser:
        # get the first line based on the first forum that this
        # admin is associated with
        admin = Admin.objects.filter(auth_user=auth_user)[0]
        forum = admin.forum
        line = forum.line_set.all()[:1]
    else:
        line = []
        
    return send_response(line)

'''
Do this below the other imports bc
broadcast mod itself imports from this file
'''
import broadcast
def survey(request):
    params = request.GET
    
    surveys = Survey.objects.filter(broadcast=True)
    if params.__contains__('lineid'):
        line_id = int(params['lineid'])
        line = get_object_or_404(Line, pk=line_id)
        surveys = Survey.objects.filter(number__in=[line.number,line.outbound_number], broadcast=True).distinct().order_by('-id')
       
    return send_response(surveys)

def bcast(request):
    params = request.POST
        
    # Get subjects
    who = params['who']
    if who == 'numbers':
        numsRaw = params['numbersarea']
        if '\n' in numsRaw:
            numbers = numsRaw.split('\n')
        if ',' in numsRaw:
            numbers = numsRaw.split(',')
        else:
            numbers = [numsRaw]
        
        subjects = broadcast.subjects_by_numbers(numbers)  
    
    elif who == 'tag':
        tagids = params.getlist('tag')
        tags = Tag.objects.filter(pk__in=tagids)
        subjects = broadcast.subjects_by_tags(tags)
    
    elif who == 'log':
        lastncallers = params['lastncallers']
        since = params['since']
        
        if lastncallers == 'ALL':
            lastncallers = 0
        else:
            lastncallers = int(lastncallers)
        since = datetime.strptime(since, '%b-%d-%Y')
        
        line_id = int(params['lineid'])
        line = get_object_or_404(Line, pk=line_id)         
        subjects = broadcast.subjects_by_log(settings.IVR_LOGFILE, line, since, lastncallers)

    # Get message
    what = params['what']
    if what == 'file':
        line_id = int(params['lineid'])
        line = get_object_or_404(Line, pk=line_id) 
        bcastfile = request.FILES['bcastfile']
        survey = broadcast.single(bcastfile, line)
    
    #elif params.__contains__('sms'):
        #TODO
    elif what == 'survey':
        surveyid = params['survey']
        survey = get_object_or_404(Survey, pk=surveyid)
        if survey.template:
            message_forum_id = int(params['messageforumid'])
            mf = get_object_or_404(Message_forum, pk=message_forum_id) 
            responseprompt = params.__contains__('response')
            survey = broadcast.thread(mf, survey, responseprompt)
        
    
    fromtime = timedelta(hours=int(params['fromtime']))
    tilltime = timedelta(hours=int(params['tilltime']))
     
    # Get schedule
    when = params['when']
    if when == 'now':
        now = datetime.now()
        start_date = datetime(year=now.year, month=now.month, day=now.day)
        nextten = now.minute - (now.minute % 10) + 10
        fromtime = timedelta(hours=now.hour, minutes = nextten)
    elif when == 'date':
        bcastdate = params['bcastdate']
        start_date = datetime.strptime(bcastdate, '%b-%d-%Y')
    
    duration = int(params['duration'])
    backups = params.__contains__("backups")

    broadcast.broadcast_calls(survey, subjects, start_date, bcast_start_time=fromtime, bcast_end_time=tilltime, duration=duration, backups=backups)
    
    if params['messageforumid']:
        return HttpResponseRedirect(reverse('otalo.AO.views.messageforum', args=(int(params['messageforumid']),)))
    else:
        return HttpResponseRedirect(reverse('otalo.AO.views.forum'))

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
            if line.outbound_number not in numbers:
                numbers.append(line.outbound_number)
                
        templates = Survey.objects.filter(template=True, number__in=numbers)
    
    return send_response(templates)

def surveyinput(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    # update the status
    survey.getstatus()
    
    # get all prompts in reverse order so that the last ones will be inserted first into the widget
    prompts = Prompt.objects.filter(survey=survey, option__action=broadcast.OPTION_RECORD).distinct().order_by('-order')
    
    return send_response(prompts, relations=('survey',))

def cancelsurvey(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    survey.status = Survey.STATUS_CANCELLED
    survey.save()
    now = datetime.now()
    Call.objects.filter(survey=survey, date__gt=now).delete()
        
    return send_response([survey])

def surveydetails(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    calls = Call.objects.filter(survey=survey).order_by('date')
    
    firstCallDate = calls.aggregate(Min('date'))
    firstCallDate = firstCallDate.values()[0]
    
    numpairs = calls.values('subject__number')
    numbers = [pair.values()[0] for pair in numpairs]
    numbers = ','.join(numbers)
    
    response = HttpResponse('[{"model":"SURVEY_METADATA", "date":"'+str(firstCallDate)+'","numbers":"'+numbers+'"}]')
    response['Pragma'] = "no cache"
    response['Cache-Control'] = "no-cache, must-revalidate"
    return response
      
def promptresponses(request, prompt_id):
    params = request.GET
    
    prompt = get_object_or_404(Prompt, pk=prompt_id)
    start = int(params['start'])
    input = Input.objects.filter(prompt=prompt)[start:start+VISIBLE_MESSAGE_COUNT]
    count = input.count()
    
    resp = send_response(input, relations={'call':{'relations':{'subject':{'fields':('name','number',)}}}, 'prompt':()} )
    
    if count > 0:
        # append some meta info about the messages
        # remove end bracket
        json = resp.content[:-1]
        json += ', {"model":"MESSAGE_METADATA", "start":'+str(start)+', "count":'+str(count)+'}]'
        resp.content = json
    
    return resp
    
def get_responders(message_forum):
    
    tags = Tag.objects.filter(message_forum = message_forum)
    
    # Find users who match at least one of the tags for this message, excluding
    # those who have already passed on this message and have listened to it beyond the listen threshold
    # (the excludes for if a question is re-run for responders), and pick the ones with the least pending questions
    responder_ids = User.objects.filter(tags__in = tags, forum = message_forum.forum).exclude(message_responder__message_forum=message_forum, message_responder__passed_date__isnull=False).exclude(message_responder__message_forum=message_forum, message_responder__listens__gt=LISTEN_THRESH).values("id").annotate(num_assigned=Count('message_responder__message_forum')).filter(num_assigned__lte=MAX_QUESTIONS_PER_RESPONDER).order_by('num_assigned')[:MAX_RESPONDERS]    
    responder_ids = [row['id'] for row in responder_ids]
    
    # don't do any minimum checking, since tags are optional and manual assignment is possible

    return User.objects.filter(id__in=responder_ids) 
  
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

    # update all nodes to the right of the child
    msgs = Message.objects.filter(rgt__gte=child.lft).exclude(pk=child.id)

    for m in msgs:
        m.rgt += 2
        if (m.lft >= child.lft):
            m.lft += 2
        m.save()
        
    child.save()

def download(request, model, model_id):
    if model == 'mf':
        mf = get_object_or_404(Message_forum, pk=model_id)
        fname = mf.message.content_file
    elif model == 'si':
        input = get_object_or_404(Input, pk=model_id)
        fname = input.input
    
    fname = settings.MEDIA_ROOT + '/' + fname
    return send_file(fname,'application/octet-stream')

from django.utils.encoding import smart_str

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


