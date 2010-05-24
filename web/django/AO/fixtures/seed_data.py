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
from otalo.AO.models import User, Forum, Tag, Admin, Line
from django.db.models import Q
from django.contrib.auth.models import User as AuthUser

CROPS = ['Cotton', 'Wheat', 'Cumin', 'Castor', 'Mustard', 'Millet', 'Groundnut', 'Maize', 'Paddy', 'Onion','Tobacco', 'Sesame', 'Chilli','Sorghum', 'Garlic', 'Brinjal', 'Gram', 'Chickpea','Banana','Papaya', 'Tumeric', 'Other' ]
TOPICS = ['Crop Planning','Seeds', 'Soil Care','Pests', 'Diseases', 'Weeding', 'Irrigation', 'Animal Husbandry', 'Harvesting', 'Marketing', 'Other']

ADMINS = {'DSC':['Admin', 'Neil', 'Paresh', 'Parina'], 'UNNATI':['Satyam']}
RESPONDERS = {'DSC':['Paresh', 'Parasara', 'Manhar Patel', 'Bharat Rajgor', 'Bharat Patel', 'Amarsinh'], 'UNNATI':['UNNATI']}

def tags():
    count = 0
        
    forums = Forum.objects.filter(Q(posting_allowed='y') | Q(responses_allowed='y'))
    for forum in forums:
        for crop in CROPS:
            t = Tag.objects.filter(tag=crop, type='agri-crop')
            if not bool(t):
               t = Tag(tag=crop, type='agri-crop')
               print ("adding " + str(t))
               t.save()
               count += 1
            else:
                t = t[0]
            forum.tags.add(t)
           
        for topic in TOPICS:
            t = Tag.objects.filter(tag=topic, type='agri-topic')
            if not bool(t):
               t = Tag(tag=topic, type='agri-topic')
               print ("adding " + str(t))
               t.save()
               count += 1
            else:
                t = t[0]
            forum.tags.add(t)
           
    print(str(count) + " new tags added.")
   
# these are web admins.
# grant them access to all the forums on their line 
def admins():
    count = 0
        
    for line_str, admin_lst in ADMINS.items():
        line = Line.objects.get(name__icontains=line_str)
        forums = Forum.objects.filter(line=line)
        for admin_str in admin_lst:
            # the admin may have multiple numbers registered
            admin = User.objects.filter(name__icontains=admin_str)[0]
            auth_user = AuthUser.objects.filter(username=admin.name)
            if not bool(auth_user):
                auth_user = AuthUser.objects.create_user(admin.name, '')
                auth_user.save()
            else:
                auth_user = auth_user[0]
            for forum in forums:
                    a = Admin(user=admin, forum=forum, auth_user=auth_user)
                    print ("adding " + str(a))
                    a.save()
                    count += 1
    
    print(str(count) + " new admin objs added.")
                
# add full capabilities to the responders listed above
def responders():
    count = 0
    
    for line_str, resp_lst in RESPONDERS.items():
        line = Line.objects.get(name__icontains=line_str)
        forums = Forum.objects.filter(line=line)
        for forum in forums:
            tags = Tag.objects.filter(forum=forum)
            for responder_str in resp_lst:
                # give capabilities to just one of the registered numbers
                responder = User.objects.filter(name__icontains=responder_str)[0]
                forum.responders.add(responder)
                for tag in tags:
                    if not (tag in responder.tags.all()):
                        responder.tags.add(tag)
                        print ("adding " + str(responder) + ": " + str(tag))
                        count += 1
       
    print(str(count) + " new responder_tag objs added.")
    
    
def main():
    tags()
    admins()
    responders()
    
main()
