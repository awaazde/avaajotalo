from otalo.ao.models import Message_forum
from haystack import indexes


class Message_forumIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    message = indexes.CharField(model_attr='message', null=True)
    forum_id = indexes.IntegerField(null=True)
    status = indexes.IntegerField(model_attr='status', null=True)
    tags = indexes.CharField(model_attr='tags', null=True)
    author_name = indexes.EdgeNgramField(null=True)
    author_number = indexes.EdgeNgramField(null=True)
    author_district = indexes.EdgeNgramField(null=True)
    author_taluka = indexes.EdgeNgramField(null=True)
    author_village = indexes.EdgeNgramField(null=True)
    message_date = indexes.DateTimeField(null=True)
    message_thread_id = indexes.IntegerField(null=True)

    def get_model(self):
        return Message_forum
    
    def index_queryset(self, using=None):
        return self.get_model().objects.all()
    
    def prepare_author_name(self, obj):
        return obj.message.user.name

    def prepare_forum_id(self, obj):
        return obj.forum.id
    
    def prepare_status(self, obj):
        return obj.status
    
    def prepare_author_number(self, obj):
        return obj.message.user.number
    
    def prepare_author_district(self, obj):
        return obj.message.user.district
    
    def prepare_author_taluka(self, obj):
        return obj.message.user.taluka
    
    def prepare_author_village(self, obj):
        return obj.message.user.village
    
    def prepare_message_date(self, obj):
        return obj.message.date
    
    def prepare_tags(self, obj):
        return [tag.tag for tag in obj.tags.all()]
    
    def prepare_message_thread_id(self, obj):
        if obj.message.thread is not None:
            return obj.message.thread.id
        else:
            return -1
    
    def get_updated_field(self):
        return "last_updated"