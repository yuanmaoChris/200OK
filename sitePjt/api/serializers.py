from rest_framework import serializers
from django.contrib.auth import get_user_model
from posting.models import Post, Comment

Author = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Author
        fields = ('displayName', 'date_joined', 'last_login',
                  'bio', 'github', 'host', 'url', 'avatar',
                  )

    def create(self, validated_data):
        return Author.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.displayName = validated_data.get(
            'displayName', instance.displayName)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.github = validated_data.get('github', instance.github)
        instance.save()
        return instance


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField('get_author')
    comments = serializers.SerializerMethodField('get_comment')

    class Meta:
        model = Post
        #get source field done plz..
        fields = ('title', 'source', 'origin',
                  'description', 'contentType', 'content',
                  'author', 'categories', 'published', 'id', 'visibility',
                  'unlisted', 'comments'
                  )

    def get_author(self, obj):
	    return AuthorSerializer(obj.author).data

    def get_comment(self, obj):
        comments = Comment.objects.filter(post=obj)
        count = len(comments)
        return CommentListSerializer(comments, context={'count': count}, exclude=['query']).data


class PostListSerializer(serializers.Serializer):
    query = serializers.SerializerMethodField('get_query')
    count = serializers.SerializerMethodField('get_count')
    posts = serializers.SerializerMethodField('get_posts')

    class Meta:
        fields = ('query', 'count', 'posts')

    def get_query(self, obj):
        return self.context.get('query')

    def get_count(self, obj):
        return self.context.get('count')

    def get_posts(self, obj):
        return PostSerializer(obj, many=True).data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField('get_author')

    def get_author(self, obj):
	    return AuthorSerializer(obj.author).data

    class Meta:
        model = Comment
        fields = ('author', 'comment', 'contentType', 'published', 'id')


class CommentListSerializer(serializers.Serializer):
    query = serializers.SerializerMethodField('get_query')
    count = serializers.SerializerMethodField('get_count')
    comments = serializers.SerializerMethodField('get_comments')

    #@ https://stackoverflow.com/questions/51904829/django-serializer-decide-which-fields-are-serialized-at-runtime
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

    class Meta:
        fields = ('query', 'count', 'comments')

    def get_query(self, obj):
        return self.context.get('query')

    def get_count(self, obj):
        return self.context.get('count')

    def get_comments(self, obj):
        return CommentSerializer(obj, many=True).data
