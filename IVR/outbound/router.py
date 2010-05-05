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
import sys
from ESL import *
from otalo.AO.models import Message, Tag, Message_tag, User, Responder_tag, Message_responder

RETRY_THRESH = 3
IVR_script = 'answer.lua'

def main():
    # TODO: check for expired reserve_untils and release them
    
    responder_ids = Responder_tag.objects.values_list('user', flat=True).distinct()
    
    for responder_id in responder_ids:
#        # need to get questions because previous responders
#        # will affect the list of questions for the subsequent caller
#        # (and maybe not require a call at all)
#        questions = get_qs_to_answer_by(responder_id)
#        
#        if questions:
        originate(responder_id, IVR_script)
            
#            for q in q_ids_set:
#                q = Message.objects.get(pk=q.id)
#                
#                if (q.rgt > 2):
#                    # question was answered
#                    answered += [q.id]

    
def originate(responder_id, script):
    # block until there's an open channel, or current calls below a threshold (using show calls command)
    con = ESLconnection('127.0.0.1', '8021', 'ClueCon')
    #are we connected?

    if con.connected():
        #run command
        #con.api("luarun " + script + " " + responder_id)
        con.api('luarun ' + script + ' user/1001')
    else:

        print 'Not Connected'
        sys.exit(2)

    # call with q_ids, answer_person_id
    
# Given a User(id)
# returns a list of message IDs            
def get_qs_to_answer_by(user_id):
    # get all pending questions that match at least one
    # of the tags associated with the ap, and order by most
    # recent message
    
    # assumes every question has at least one tag, or else we should append message_ids with
    # the msg attrs below but that don't appear in Message_tag
    
    #tag_ids = Responder_tag.objects.filter(user = user_id).values_list('tag', flat=True)
    #return Message_tag.objects.filter(message__lft=1, message__rgt=2, message__routable='y', message__retries__lte=RETRY_THRESH, tag__in=tag_ids).values_list('message', flat=True).order_by('-message__date')
    return Message_responder.objects.filter(message__lft=1, message__rgt=2, user=user_id, listens__lt=RETRY_THRESH)