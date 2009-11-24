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
    name = models.CharField(max_length=128)
    district = models.CharField(max_length=128)
    taluka = models.CharField(max_length=128)
    village = models.CharField(max_length=128)
    name_file = models.CharField(max_length=24)
    district_file = models.CharField(max_length=24)
    taluka_file = models.CharField(max_length=24)
    village_file = models.CharField(max_length=24)

    def __unicode__(self):
        return self.name + '-' + self.number

class Message(models.Model):
    date = models.DateTimeField()
    content_file = models.CharField(max_length=48)
    extra_file = models.CharField(max_length=48)
    status = models.IntegerField()
    position = models.IntegerField()
    user = models.ForeignKey(User)
    forum = models.ForeignKey(Forum)
    lft = models.IntegerField(default=1) 
    rgt = models.IntegerField(default=2)
    thread = models.ForeignKey('self', blank=True, null=True)

    def __unicode__(self):
        return str(self.date) + '_' + self.user.name + '_' + self.forum.name
