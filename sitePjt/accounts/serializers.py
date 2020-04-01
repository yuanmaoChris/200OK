from rest_framework import serializers
from django.contrib.auth import get_user_model

Author = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('get_id')

    class Meta:
        model = Author
        fields = ('id', 'displayName','github', 'host', 'url',
                  )

    def get_id(self, obj):
        return "{}author/{}".format(str(obj.host), str(obj.id))
        
    # def create(self, validated_data):
    #     return Author.objects.create(**validated_data)

    # def update(self, instance, validated_data):
    #     instance.displayName = validated_data.get('displayName', instance.displayName)
    #     instance.bio = validated_data.get('bio', instance.bio)
    #     instance.github = validated_data.get('github', instance.github)
    #     instance.save()
    #     return instance


class CommentAuthorSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('get_id')
    url = serializers.SerializerMethodField('get_url')

    class Meta:
        model = Author
        fields = ('id', 'url', 'host', 'displayName', 'github',
                  )

    def get_id(self, obj):
        return str(obj.host) + '/author/' + str(obj.id)

    def get_url(self, obj):
        return str(obj.host) + '/author/' + str(obj.id)
