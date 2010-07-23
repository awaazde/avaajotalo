from django.db import models
from django.contrib.auth.models import User as AuthUser
from otalo.AO.models import User

class Notification(models.Model):
    """Contains all the information for a notification
    """
    # title/name of that notification
    name =              models.CharField(max_length=256, blank=False,null=False)
    # function name xxx present in notification.notification_utils as 
    #'trigger_xxx'
    # trigger_function =  models.CharField(max_length=256, null=False) 
    # function name yyy present in notification.notification_utils as 
    #'action_yyy'
    action_function =   models.CharField(max_length=256, null=False) 
    # date this notification was created
    created_on =        models.DateTimeField(auto_now_add=True, null=False) 
    # date this notification was modified
    updated_on =        models.DateTimeField(auto_now=True, null=False) 
    # second template field for the content (email content or sms content)
    template_content =  models.TextField(blank=True, null=True) 
    
    users =             models.ManyToManyField(User, through="NotificationUser",
    related_name="notifications")
    
    def __unicode__(self):
        return "[Notification: " + ", ".join([self.name, 
                 self.template_content]) + "]"

class NotificationUser(models.Model):
    """Attribution of a notification to a user
    """
    notification =      models.ForeignKey(Notification)
    user =              models.ForeignKey(User)
    created_on =        models.DateTimeField(auto_now_add=True)
    active =            models.IntegerField(default=1) # 0=inactive 1=active
    
    def __unicode__(self):
        return "[NotificationUser: "+", ".join([unicode(self.notification.name), 
                self.user.number, self.active and "active" or "inactive" ]) +"]"

class NotificationMessage(models.Model):
    """ Individual messages that have to be sent to the user
    """
    user =              models.ForeignKey(User)
    created_on =        models.DateTimeField(auto_now_add=True)
    sent_on =           models.DateTimeField(null=True, blank=True)
    # typ: 0 sms, 1 voice
    typ =               models.IntegerField(null=False)
    number =            models.CharField(max_length=255, null=False)
    # for when typ==0
    text_message =      models.CharField(max_length=255, null=True, blank=True)
    # for when typ=1
    voice_message_number = models.IntegerField(null=True, blank=True)
    voice_message_tag = models.CharField(max_length=50,null=True, blank=True)
    # 1 if there was an error
    error =             models.IntegerField(null=False, default=0)
    

class Setting(models.Model):
    """Some setting information
    """
    name =              models.CharField(max_length=255, blank=False, null=False)
    value =             models.CharField(max_length=255, blank=False, null=False)
    value_type =        models.CharField(max_length=30, blank=False, null=False, 
                        default="str")
    def __unicode__(self):
        return "[NotificationSetting] %s=%s (%s)"%(self.name, self.value, 
        self.value_type)

