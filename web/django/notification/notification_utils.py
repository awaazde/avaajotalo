from otalo.AO.models import Forum, Message, Message_forum, User, Tag
from otalo.AO.models import Message_responder, Admin
from otalo.notification.models import Notification, NotificationUser, Setting
from otalo.notification.models import NotificationMessage

__all__=["process_notification",]

def process_notification(message, parent_message_forum):
    """Get the tags of the message, and sends a notification of the type
    defined for each user when the user has sent a question with a 
    similar tag.
    We do not send more than one message to a user.
    """
    if parent_message_forum is None or parent_message_forum.message is None:
        return
    # print "CHECK notification", message
    # print "parent", parent_message_forum
    tags = parent_message_forum.tags.all()
    # print "TAGS", tags
    users_done = []
    for tag in tags:
        # take all the users who have asked a question with the same tag
        for pm_forum in tag.message_forum_set.all():
            # print "PM forum", pm_forum
            # get the user from the original question
            user = pm_forum.message.user
            # print "USER ", user
            notifications = user.notifications.filter(notificationuser__active__exact=1)
            # if the user has no notification at all, we give him one
            if notifications.count()==0:
                # print "GET USER NOTIFIC STYLE"
                notifications = get_roundrobin_notification(user)
            # check that we're not sending a message to the same user
            if user in users_done:
                # print "USER DONE ALREADY"
                continue
            users_done.append(user)
            # print "Notifications for user", notifications
            # Process each notification that is active
            for notific in notifications:
                action_func = __get_function__("action_%s"%notific.action_function)
                # create a notification message of the given style
                action_func(user, notific, tag)
        


def __get_function__(func):
    """Returns the function object corresponding to the given func name
    """
    return globals().get(func, None)

###############################################################################
# Action functions

def action_detailed_sms_to_user(user, notification, tag):
    """ Send an SMS to every user who has asked a question with the same
    tag
    """
    # create a notification message
    msg = NotificationMessage()
    msg.user = user
    msg.typ = 0
    msg.number = user.number
    msg.text_message = notification.template_content%tag.tag
    msg.save()

    
def action_flash_call(message, parent_message_forum, notification):
    """Calls the user flash mode"""
    # TO DO XXXXX NOT USED NOW
    pass
    
def action_no_action(message, parent_message_forum, notification):
    """No action is taken"""
    return

def action_voice_call(user, notification, tag):
    """Create a voice call NotificationMessage for the user with the given
    tag
    """
    msg = NotificationMessage()
    msg.user = user
    msg.typ = 1
    msg.number = user.number
    # msg.voice_message_number # not used yet - would need grouping on user
    msg.voice_message_tag = tag.tag
    msg.save()
    
###############################################################################
# other

def send_sms(phone_number, content):
    """Send an SMS to the given phone_number and the text message is given
    in content. 
    NOT USED HERE. sms_utils is called from IVR/outbound/notifications.py
    """
    print "SMS to %s:"%phone_number
    print "\t", content
    from otalo.notification import sms_utils
    ok = sms_utils.send_sms(phone_number, content, sms_utils.OVI_NUM_FROM)
    print "SMS SENT"

def get_roundrobin_notification(user):
    """ Select the notification that should be given to the next user. 
    Update the value so that the next user is given the next notification style
    """
    settings = Setting.objects.filter(name='notification_roundrobin').all()
    setting = settings and settings[0] or None
    value = None
    selected_notification = []
    if setting:
        try:
            value = int(setting.value)
        except Exception, e:
            raise Exception("Notification error, the value set for notification_roundrobin Setting is not an integer")
    else:
        raise Exception("Notification error, there is not notification_roundrobin Setting")
    if value is not None:
        notifications = Notification.objects.order_by("id").all()
        count = notifications.count()
        if value>=count:
            value = 0
        if value<count:
            nu = NotificationUser()
            selected_notification = notifications[value]
            nu.notification = notifications[value]
            nu.user = user
            nu.save()
        value += 1
        if value>=count:
            value=0
        setting.value = str(value)
        setting.save()
    return [selected_notification, ]
            

