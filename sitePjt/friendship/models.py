from django.db import models
from accounts.models import Author
import uuid

# Create your models here.


class FriendRequest(models.Model):
    author_from = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='author_from')
    author_to = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='author_to')
    is_approved = models.BooleanField(default="False")
    
class Friendship(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author_a = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='author_a')
    author_b = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='author_b')
    
