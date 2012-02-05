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
from urllib import urlencode
import httplib2
import datetime
from otalo.AO.models import Line, User
from otalo.sms.models import Config, ConfigParam, SMSMessage

def send_sms(from_line, recipients, content, date=None):
    config = from_line.sms_config
    
    sender = User.objects.filter(number=from_line.number)
    if bool(sender):
        sender = sender[0]
    else:
        sender = User(number=from_line.number, allowed='y')
        sender.save()
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
        data[config.date_param_name] = date_str
    params = ConfigParam.objects.filter(config=config)
    for param in params:
        data[param.name] = param.value
        
    http = httplib2.Http()
    resp, content = http.request(config.url, "POST", headers=Config.HEADER, body=urlencode(data) )
    #print "SMS TO GATEWAY HTTP", resp, content
    #print "SMS TO GATEWAY ", data
    return True


if __name__=="__main__":
    line = Line.objects.get(pk=1)
    users = User.objects.filter(pk__in=[1,2])
    print(str(users))
    send_sms(line,users,"Testing again from Neil/Awaaz.De. Thanks!!")
    
    
    