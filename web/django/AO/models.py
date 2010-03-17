from django.db import models

class Forum(models.Model):
    name = models.CharField(max_length=24)
    name_file = models.CharField(max_length=24)
    moderated = models.CharField(max_length=1)
    posting_allowed = models.CharField(max_length=1)
    responses_allowed = models.CharField(max_length=1)
    open = models.CharField(max_length=1)
    maxlength = models.IntegerField()

    def __unicode__(self):
        return self.name


class User(models.Model):
    number = models.CharField(max_length=24)
    allowed = models.CharField(max_length=1)
    admin = models.CharField(max_length=1)
    name = models.CharField(max_length=128, blank=True, null=True)
    district = models.CharField(max_length=128, blank=True, null=True)
    taluka = models.CharField(max_length=128, blank=True, null=True)
    village = models.CharField(max_length=128, blank=True, null=True)
    name_file = models.CharField(max_length=24, blank=True, null=True)
    district_file = models.CharField(max_length=24, blank=True, null=True)
    taluka_file = models.CharField(max_length=24, blank=True, null=True)
    village_file = models.CharField(max_length=24, blank=True, null=True)

    def __unicode__(self):
        if self.name:
            return self.name + '-' + self.number
        else:
            return self.number

class Message(models.Model):
    date = models.DateTimeField()
    content_file = models.CharField(max_length=48)
    summary_file = models.CharField(max_length=48)
    user = models.ForeignKey(User)    
    thread = models.ForeignKey('self', blank=True, null=True)
    lft = models.IntegerField(default=1) 
    rgt = models.IntegerField(default=2)

    def __unicode__(self):
        return str(self.date) + '_' + unicode(self.user)
 
class Message_forum(models.Model):
    message = models.ForeignKey(Message)
    forum = models.ForeignKey(Forum)
    status = models.IntegerField()
    position = models.IntegerField(blank=True, null=True)
    
    def __unicode__(self):
        return unicode(self.message) + '_' + unicode(self.forum)
    
class Tag(models.Model):
    tag = models.CharField(max_length=24)
    type = models.CharField(max_length=24, blank=True, null=True)
    tag_file = models.CharField(max_length=24, blank=True, null=True)
    
    def __unicode__(self):
        return self.tag
    
class Message_tag(models.Model):
    message = models.ForeignKey(Message)
    tag = models.ForeignKey(Tag)
    
    def __unicode__(self):
        return unicode(self.message) + '_' + unicode(self.tag)