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


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField('get_author')
    comments = serializers.SerializerMethodField('get_comment')
    
    class Meta:
        model = Post
        fields = ('title', 'source', 'origin', 
                    'description', 'contentType','content',
                    'author', 'published', 'visibility',
                    'categories', 'unlisted', 'comments'
                    )

    def get_author(self, obj):
	    return AuthorSerializer(obj.author).data

    def get_comment(self, obj):
        comments = Comment.objects.filter(post=obj)
        return CommentSerializer(comments, many=True).data



class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField('get_author')

    def get_author(self, obj):
	    return AuthorSerializer(obj.author).data

    class Meta:
        model = Comment
        fields = ('contentType', 'comment',
                  'author', 'published',
                  )
