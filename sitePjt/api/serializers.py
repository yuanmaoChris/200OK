from rest_framework import serializers
from django.contrib.auth import get_user_model
from posting.models import Post, Comment

Author = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('get_id')
    url = serializers.SerializerMethodField('get_url')

    class Meta:
        model = Author
        fields = ('id', 'displayName', 'github', 'host', 'url',
                  )

    def get_id(self, obj):
        return "{}/author/{}/".format(str(obj.host), str(obj.id))

    def get_url(self, obj):
        return "{}/author/{}/".format(str(obj.host), str(obj.id))

    # def create(self, validated_data):
    #     return Author.objects.create(**validated_data)

    # def update(self, instance, validated_data):
    #     instance.displayName = validated_data.get(
    #         'displayName', instance.displayName)
    #     instance.bio = validated_data.get('bio', instance.bio)
    #     instance.github = validated_data.get('github', instance.github)
    #     instance.save()
    #     return instance

class PostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField('get_author')
    comments = serializers.SerializerMethodField('get_comment')
    origin = serializers.SerializerMethodField('get_origin')
    categories = serializers.SerializerMethodField('get_categories')
    description = serializers.CharField(max_length=200,default='No description')
    visibleTo = serializers.StringRelatedField(many=True)
    count = serializers.SerializerMethodField('get_count')
    size = serializers.SerializerMethodField('get_size')
    next = serializers.SerializerMethodField('get_next')
    class Meta:
        model = Post
        #get source field done plz..
        fields = ('title', 'source', 'origin', 'description', 'contentType', 'content',
                  'author', 'categories', 'published', 'id', 'visibility',
                  'unlisted', "count", "size", "next", 'comments', 'visibleTo',
                  )

    def get_author(self, obj):
        return AuthorSerializer(obj.author).data
    
    def get_origin(self, obj):
        return "{}/posts/{}".format(str(obj.author.host), str(obj.id))
    
    def get_categories(self, obj):
        categories = obj.categories.split("#")
        return categories[1:]
    
    def get_count(self, obj):
        comments = Comment.objects.filter(post=obj)
        return len(comments)

    def get_size(self, obj):
        return 5

    def get_next(self, obj):
        return "{}/posts/{}/comments".format(str(obj.author.host), str(obj.id))

    def get_comment(self, obj):
        comments = Comment.objects.filter(post=obj).order_by("-published")[:5]
        return CommentSerializer(comments, many=True).data
    
    def create(self, validated_data):
        validated_data['author'] = self.context.get('author')
        return Post.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.source = validated_data.get('source', instance.source)
        instance.origin = validated_data.get('origin', instance.origin)
        instance.contentType = validated_data.get('contentType', instance.contentType)
        instance.content = validated_data.get('content', instance.content)
        instance.categories = validated_data.get('categories', instance.categories) 
        instance.published = validated_data.get('published', instance.published)
        instance.id = validated_data.get('id', instance.id)
        instance.visibility = validated_data.get('visibility', instance.visibility)
        instance.unlisted = validated_data.get('unlisted', instance.unlisted)
        instance.save()
        return instance
        
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField('get_author')

    def get_author(self, obj):
     return AuthorSerializer(obj.author).data

    class Meta:
        model = Comment
        fields = ('author', 'comment', 'contentType', 'published', 'id')

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
