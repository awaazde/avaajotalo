import router
from datetime import datetime, timedelta
from otalo.surveys.models import Call, Subject
from otalo.notification.models import NotificationMessage
from otalo.notification import sms_utils

# This should match with how often the cron runs
INTERVAL_MINS =     10
IVR_SCRIPT =        'AO/outbound/notification_voice.lua'
# should match the var in IVR_SCRIPT
CALLID_VAR_VAL =    'ao_notification true'
# this script
SCRIPT =            "notifications.py / notification_voice.lua:"

def deliver_notifications():
    # get all messages that have not been sent
    users_done = [] # not many voice calls to the same one
    for notmsg in NotificationMessage.objects.filter(sent_on__isnull=True).all():
        if notmsg.user in users_done:
            continue
        users_done.append(notmsg.user)
        # SMS
        if notmsg.typ == 0: 
            ok = sms_utils.send_sms(notmsg.number, notmsg.text_message, sms_utils.OVI_NUM_FROM)
            if not ok:
                notmsg.error = 2
            notmsg.sent_on = datetime.now()
            notmsg.save()
        # voice call
        elif notmsg.typ==1:
            make_voice_call(notmsg.id)
            # the lua script updates the sent_on field

def make_voice_call(notmsg_id):
    outbound_var_val=False
    con = ESLconnection('127.0.0.1', '8021', 'ClueCon')
    if not con.connected():
    	print 'Not Connected'
    	sys.exit(2)
    def _get_n_channels(_con):
        e = _con.api("show channels")
        chan_txt = e.getBody()
        n_chans_txt = chan_txt[chan_txt.rindex('total.')-3:chan_txt.rindex('total.')-1]
        return int(n_chans_txt)
    # this is precautionary in order to kill any rogue calls
    # but it means you have to be sure that there are no outbound
    # calls open at this time that you shouldn't be killing
    if outbound_var_val:
        print(SCRIPT + "attempting to kill open channels")
        con.api("hupall normal_clearing " + outbound_var_val)
        # for good measure, sleep a bit and do it again
        time.sleep(5)
        con.api("hupall normal_clearing " + outbound_var_val)
        # let it marinate before calling out
        time.sleep(5)        
    num_channels = _get_n_channels(con)
    sleep_secs = 2
    while num_channels >= MAX_CHANNELS:
        #sleep for a while
        print(SCRIPT + "too many channels: " + str(num_channels) + ", sleeping for " + str(sleep_secs) + "s")
        time.sleep(sleep_secs)
        num_channels = _get_n_channels(con)
        sleep_secs *= 2	
    print(SCRIPT + 'running ' + IVR_script + ' (' + str(notmsg_id) + ')')
    con.api("luarun " + IVR_script + " " + str(notmsg_id))
    # sleep a bit to let the call register with FS
    time.sleep(2)
    
          
def main():
   deliver_notifications()

if __name__=="__main__":
    main()
