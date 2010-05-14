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
import router
from datetime import datetime
from otalo.AO.models import Message_responder

IVR_SCRIPT = 'AO/outbound/responder.lua'

def main():
    # check for expired reserve_untils and release them
    now = datetime.now()
    Message_responder.objects.filter(reserved_until__lt=now).update(reserved_by=None, reserved_until=None)

    # get every possible responder and let the script figure out which messages to play, etc.
    responder_ids = Message_responder.objects.values_list('user', flat=True).distinct()
    router.route_calls(responder_ids, IVR_SCRIPT)

main()
