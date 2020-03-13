from rest_framework import serializers
from .models import *


class FriendRequestSerializer(serializers.ModelSerializer):

	pub_date = serializers.DateTimeField('date posted', auto_now_add=True, blank=True)
	is_approved = serializers.BooleanField(default="False")

	class Meta:
		model = FriendRequest
		fields = ('author_from', 'author_to', 'pub_date', 'is_approved')

class FriendshipSerializer(serializers.ModelSerializer):

	id = serializers.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

	class Meta:
		model = FriendRequest
		fields = ('id', 'author_a', 'author_b')

