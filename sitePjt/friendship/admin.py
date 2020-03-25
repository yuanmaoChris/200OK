from django.contrib import admin

# Register your models here.
from .models import FriendRequest, Friendship, Friend

admin.site.register(FriendRequest)
admin.site.register(Friendship)
admin.site.register(Friend)
