from django.db import models
from accounts.models import Author
from django.db.models import Q
import uuid

# Create your models here.


class Friend(models.Model):
    id = models.CharField(primary_key=True,max_length=100)
    displayName = models.CharField(max_length=20)
    host = models.CharField(max_length=100)
    url = models.CharField(max_length=100)

    def __str__(self):
        return self.displayName

class FriendRequest(models.Model):
    '''
    namely a friend request model between authors
    '''
    author_from = models.ForeignKey(Friend, on_delete=models.CASCADE, related_name="author_from")
    author_to = models.ForeignKey(Friend,on_delete=models.CASCADE,related_name="author_to")
    published = models.DateTimeField('date posted', auto_now_add=True, blank=True)

    def __str__(self):
        return "From: " + self.author_from.displayName + "   To: " + self.author_to.displayName
    
class Friendship(models.Model):
    '''
	namely a friendship model between authors
	Notice: For the purpose of preventing from redundant savings, we always assume author_a has a smaller author_id comparing to author_b;
			To see building friendship, goto views.py line 81-92
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author_a = models.ForeignKey(Friend, on_delete=models.CASCADE, related_name="author_a")
    author_b = models.ForeignKey(Friend,on_delete=models.CASCADE,related_name="author_b")

    def __str__(self):
        return "A: " + self.author_a.displayName + " |   B: " + self.author_b.displayName
