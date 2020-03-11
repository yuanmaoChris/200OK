from rest_framework import serializers
from .models import *


class FriendRequestSerializer(serializers.ModelSerializer):
	class Meta:
		model = FriendRequest
		fields = ('author_from', 'author_to', 'pub_date', 'is_approved')

class FriendshipSerializer(serializers.ModelSerializer):

	class Meta:
		model = FriendRequest
		fields = ('id', 'author_a', 'author_b')

