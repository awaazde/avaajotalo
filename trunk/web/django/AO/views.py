from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from otalo.AO.models import Forum, Message, User
from django.core import serializers
from django.conf import settings
from datetime import datetime
import os, stat

json_serializer = serializers.get_serializer("json")()

# Code in order of how they are declared in Message.java
MESSAGE_STATUS_PENDING = 0
MESSAGE_STATUS_APPROVED = 1

AUDIO_FILE_EXTENSION = ".mp3"

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

    if (params.__contains__('status')):
        messages = Message.objects.filter(forum=forum_id, status=params['status']).order_by('-position')
    else:
        messages = Message.objects.filter(forum=forum_id).order_by('-date')
    return send_response(messages, ('user',))

def message(request, message_id):
    # Note use of filter instead of get to return a query set
    message = get_list_or_404(Message, pk=message_id)
    return send_response(message, ('forum',))

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

    m = get_object_or_404(Message, pk=params['messageid'])
    if m.position == -1 and params.__contains__('approve'):  # newly approving
        m.status = MESSAGE_STATUS_APPROVED
        # set the position to be the highest based
        # on what else is approved in this forum
        count = Message.objects.filter(forum = m.forum, status = MESSAGE_STATUS_APPROVED).count()
        # positions are 1-based, with highest index being the top of the list
        m.position = count + 1
    elif m.position > -1 and not(params.__contains__('approve')): # newly rejecting
        # bump down the position of everyone ahead
        ahead = Message.objects.filter(forum = m.forum, status = MESSAGE_STATUS_APPROVED, position__gt=m.position)
        for msg in ahead:
            msg.position -= 1
            msg.save()

        m.status = MESSAGE_STATUS_PENDING
        m.position = -1

    m.save()

    # Check to see if there was a response uploaded
    if request.FILES:
        f = request.FILES['response']
        resp = createmessage(m.forum, f, parent=m)

    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse('otalo.AO.views.message', args=(int(m.id),)))

def movemessage(request):
    params = request.POST
    direction = params['direction']    

    m = get_object_or_404(Message, pk=params['messageid'])
    count = Message.objects.filter(forum = m.forum, status = MESSAGE_STATUS_APPROVED).count()

    if direction == 'up' and m.position < count:
        # get the message above
        above = Message.objects.get(forum = m.forum, position = m.position+1)
        above.position -= 1
        m.position += 1

        above.save()
        m.save()
    elif direction == 'down' and m.position > 1:
        # get the message below
        below = Message.objects.get(forum = m.forum, position = m.position-1)
        below.position += 1
        m.position -= 1

        below.save()
        m.save()

    return HttpResponseRedirect(reverse('otalo.AO.views.message', args=(m.id,)))
        
def uploadmessage(request):
    if request.FILES:
        main = request.FILES['main']
        extra = False
        if 'extra' in request.FILES:
            extra = request.FILES['extra']

        f = get_object_or_404(Forum, pk=request.POST['forumid'])
        m = createmessage(f, main, extra)

        return HttpResponseRedirect(reverse('otalo.AO.views.message', args=(m.id,)))

def createmessage(forum, content, extra=False, parent=False):
    t = datetime.now()
    extra_filename = ''

    extension = content.name[content.name.index('.'):]
    filename = t.strftime("%m-%d-%Y_%H%M%S") + extension
    filename_abs = settings.MEDIA_ROOT + '/' + filename
    destination = open(filename_abs, 'wb')
    for chunk in content.chunks():
        destination.write(chunk)
    os.chmod(filename_abs, 0644)
    destination.close()

    if extra:
        extension = extra.name[extra.name.index('.'):]
        extra_filename = t.strftime("%m-%d-%Y_%H%M%S") + '_extra' + extension
        extra_filename_abs = settings.MEDIA_ROOT + '/' + extra_filename
        destination = open(extra_filename_abs, 'wb')
        for chunk in extra.chunks():
            destination.write(chunk)
        os.chmod(extra_filename_abs, 0644)
        destination.close()

    # create a new message for this content
    admin = get_console_user()
    pos = Message.objects.filter(forum = forum, status = MESSAGE_STATUS_APPROVED).count() + 1

    resp_msg = Message(date=t, content_file=filename, extra_content_file=extra_filename, status=MESSAGE_STATUS_APPROVED, position=pos, user=admin, forum=forum)

    if parent:
        add_child(resp_msg, parent)

    resp_msg.save()

    # can only set to yourself after you've saved
    if not parent:
        resp_msg.thread = resp_msg
        #resp_msg.save()

    return resp_msg

def thread(request, message_id):
    m = get_object_or_404(Message, pk=message_id)
    if m.lft == 1: # this is the parent thread
        top = m
    else:
        top = m.thread
    thread_msgs = Message.objects.filter(thread=top).order_by('lft')
    return send_response (thread_msgs, {'user':{'fields':('name', 'number',)}, 'forum':{'fields':('pk')}})

# this should return the person logged in.
# Stub it for now.
def get_console_user():
    try:
        return User.objects.get(name__contains="ADMIN")
    except User.DoesNotExist:
        # create
        u = User(number='9999999999', name="ADMIN")
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
    msgs = Message.objects.filter(rgt__gte=child.lft).exclude(id=child.id)

    for m in msgs:
        m.rgt += 2
        if (m.lft >= child.lft):
            m.lft += 2
        m.save()

def send_response(query_set, relations=()):
    response = HttpResponse(json_serializer.serialize(query_set, relations=relations))
    response['Pragma'] = "no cache"
    response['Cache-Control'] = "no-cache, must-revalidate"
    return response;


