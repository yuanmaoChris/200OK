from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
class Post(models.Model):
    POST_VISIBILITY = (
        ('PUBL', 'Public'),
        ('PRTS', 'Prviate to self'),
        ('PRTF', 'Private to friends'),
        ('PTFF', 'Private to friends of friends'),
        ('PTFL', 'Private to local friends'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    pub_date = models.DateTimeField(
        'date posted', auto_now_add=True, blank=True)
    visibility = models.CharField(max_length=4, default = 'PUBL', choices=POST_VISIBILITY)

class Follow(models.Model):
    follower_id = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name='AID1')
    be_followed_id = models.ForeignKey(User, editable=False, on_delete=models.CASCADE,related_name='AID2')
