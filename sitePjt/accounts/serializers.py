from rest_framework import serializers
from django.contrib.auth import get_user_model

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
