from rest_framework import serializers
from .models import *


class AuthorSerializer(serializers.ModelSerializer):
	
	id = serializers.SerializerMethodField('get_id')

	def get_id(self, obj):
		return "http://service/author/" + obj.uuid_str

	class Meta:
		model = Post
		fields = ('id', 'host', 'displayName', 'url', 'content', 'github', 'bio')
