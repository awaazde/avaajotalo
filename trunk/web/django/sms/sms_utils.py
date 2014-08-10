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
from decimal import Decimal
from django.db.models import F
from openpyxl.reader.excel import load_workbook
from urllib import urlencode
import httplib2
from datetime import datetime
from otalo.ao.models import Line, User, Transaction
from otalo.sms.models import Config, ConfigParam, SMSMessage

# in credits
DEF_CHARGE_PER_SMS = .5
SMS_DISALLOW_BALANCE_THRESH = 0 

def send_sms_from_line(from_line, recipients, content, date=None):
    sender = User.objects.filter(number=from_line.number)
    if bool(sender):
        sender = sender[0]
    else:
        sender = User.objects.create(name=from_line.name, number=from_line.number, allowed='y')
    
    send_sms(from_line.sms_config, recipients, content, sender, date)
    
def send_sms(config, recipients, content, sender, date=None):
    if date:
        msg = SMSMessage.objects.create(sender=sender,sent_on=date,text=content)
    else:
        msg = SMSMessage.objects.create(sender=sender,text=content)
        
    for u in recipients:
        msg.recipients.add(u)
        
    recipients_str = [(config.country_code or '')+ u.number for u in recipients]
    recipients_str = ",".join(recipients_str)
        
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

'''
'    Send different SMSs to different recipients on the same api call
'    
'    ASSUMES recipients and texts are of same length
'''
def send_multiple_sms(config, recipients, texts, sender, date=None):
    if len(recipients) != len(texts):
        return False
    
    csv=''
    for i in range(len(recipients)):
        u = recipients[i]
        text = texts[i]
        if date:
            msg = SMSMessage(sender=sender,sent_on=date,text=text)
        else:
            msg = SMSMessage(sender=sender,text=text)
        msg.save()
        msg.recipients.add(u)
        csv += (config.country_code or '')+ u.number +',"'+text+'"\n'  
        
    data = {config.text_param_name:csv}
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

def charge_sms_credits(user, num_sms, date=None, credits_per_sms=DEF_CHARGE_PER_SMS):
    if user.balance != Decimal(str(User.UNLIMITED_BALANCE)):
        amount = Decimal(credits_per_sms * num_sms)
        xact = Transaction.objects.create(user=user, type=Transaction.SMS, amount=amount)
        '''
        ' NOTE: This should only be set from testing programs.
        ' In production setting this value will throw an error
        ' since Transaction.date is immutable
        '''
        if date:
            xact.date = date
            xact.save()
        print("Created xact "+str(xact))
        # Make update atomic with F() function
        User.objects.filter(pk=user.id).update(balance = F('balance') - amount)

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
    users = User.objects.filter(pk__in=[783,223])
    texts = ['message for Jay', 'message for Neil']
    config = Config.objects.get(pk=2)
    print(str(users))
    #send_sms(line,users,"Testing again from Neil/Awaaz.De. Thanks!!")
    send_multiple_sms(config, users, texts, users[0])
    
    
    