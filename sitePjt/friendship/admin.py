from django.contrib import admin

# Register your models here.
from .models import FriendRequest, Friendship

admin.site.register(FriendRequest)
admin.site.register(Friendship)
