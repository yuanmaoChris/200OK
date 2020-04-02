from rest_framework import serializers
from .models import *

class FriendshipSerializer(serializers.Serializer):
    query = serializers.SerializerMethodField('get_query')
    author = serializers.SerializerMethodField('get_author')
    authors = serializers.SerializerMethodField('get_authors')

    class Meta:
        fields = ('query', 'author', 'authors')

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)
        if fields is not None and exclude is not None:
            serializers.ValidationError(
                "fields and exclude are simultaneously not allowed")
        super().__init__(*args, **kwargs)
        if exclude:
            for item in set(exclude):
                self.fields.pop(item, None)
        if fields:
            for item in set(self.fields.keys()) - set(fields):
                self.fields.pop(item, None)

    def get_authors(self, obj):
	    return obj

    def get_author(self, obj):
	    return self.context.get('author')

    def get_query(self, obj):
        return "friends"


class FriendSerializer(serializers.ModelSerializer):

    class Meta:
        model = Friend
        fields = ('id', 'displayName', 'host', 'url',
                  )