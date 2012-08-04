'''
    Copyright (c) 2009 Regents of the University of California, Stanford University, and others
 
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
 
        http://www.apache.org/licenses/LICENSE-2.0
 
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''
from datetime import datetime
from openpyxl.reader.excel import load_workbook
from urllib import urlencode
import httplib2
from datetime import datetime
from otalo.ao.models import Line, User
from otalo.sms.models import Config, ConfigParam, SMSMessage

def send_sms_from_line(from_line, recipients, content, date=None):
    sender = User.objects.filter(number=from_line.number)
    if bool(sender):
        sender = sender[0]
    else:
        sender = User.objects.create(name=from_line.name, number=from_line.number, allowed='y')
    
    send_sms(from_line.sms_config, recipients, content, sender, date)
    
def send_sms(config, recipients, content, sender, date=None):
    if date:
        msg = SMSMessage(sender=sender,sent_on=date,text=content)
    else:
        msg = SMSMessage(sender=sender,text=content)
    msg.save()
    recipients_str = ''
    for u in recipients:
        msg.recipients.add(u)
        recipients_str += (config.country_code or '')+ u.number +','
    recipients_str = recipients_str[:-1]
    data = {config.to_param_name:recipients_str, config.text_param_name:content}
    if date and config.date_param_format:
        date_str = date.strftime(config.date_param_format)
        #print ("date str="+date_str)
        data[config.date_param_name] = date_str
    params = ConfigParam.objects.filter(config=config)
    for param in params:
        data[param.name] = param.value
        
    http = httplib2.Http()
    resp, content = http.request(config.url, "POST", headers=Config.HEADER, body=urlencode(data) )
    #print "SMS TO GATEWAY HTTP", resp, content
    #print "SMS TO GATEWAY ", data
    return True

#DND_FILE=''
#def updateDND():
#    wb = load_workbook(filename = DND_FILE)
#    dnd_numbers = wb.get_sheet_by_name(wb.get_sheet_names()[0])
#    
#    for row in dnd_numbers.rows:
#        number = row[0].strip()[-10:]
#        user = User.objects.filter(number=number)
#        if bool(user):
#            user = user[0]
#        else:
#            user = User(number=number, allowed='y')
#            user.save()
#        
#        dnd = DoNotCall.objects.filter(user=user)
#        if bool(dnd):
#            dnd = dnd[0]
#        else:
#            call = row[1]
#            dnd = DoNotCall(user=user,call=call)
#            dnd.save()
#        
#        dnd.banking = row[2]
#        dnd.realestate = row[3]
#        dnd.education = row[4]
#        dnd.health = row[5]
#        dnd.consumergoods = row[6]
#        dnd.tourism = row[7]
#        dnd.communication = row[8]
#        
#        dnd.save()
        
        
if __name__=="__main__":
    line = Line.objects.get(pk=1)
    users = User.objects.filter(pk__in=[1,2])
    print(str(users))
    send_sms(line,users,"Testing again from Neil/Awaaz.De. Thanks!!")
    
    
    