from django.db import models
from accounts.models import Author
from django.db.models import Q
import uuid

# Create your models here.

'''
	namely a friend request model between authors
'''
class FriendRequest(models.Model):
    author_from = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='author_from')
    author_to = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='author_to')
    pub_date = models.DateTimeField('date posted', auto_now_add=True, blank=True)
    
'''
	namely a friendship model between authors
	Notice: For the purpose of preventing from redundant savings, we always assume author_a has a smaller author_id comparing to author_b;
			To see building friendship, goto views.py line 81-92
'''
class Friendship(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author_a = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='author_a')
    author_b = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='author_b')
    

