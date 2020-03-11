from django.db import models
from accounts.models import Author
import uuid

# Create your models here.
class Post(models.Model):
    POST_VISIBILITY = (
        ('PUBLIC', 'Public'),
        ('PRIVATE', 'Prviate to self'),
        ('FRIENDS', 'Private to friends'),
        ('FOAF', 'Private to friends of friends'),
        ('SERVERONLY', 'Private to local friends'),
    )
    CONTENT_TYPE = {
        ('text', 'text/plain'),
        ('md', 'text/markdown'),
    }

    UNLISTED = {
        (True, 'True'),
        (False, 'False'),
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content_type = models.CharField(max_length=4, default = 'text', choices=CONTENT_TYPE)
    content = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    unlisted = models.BooleanField(default=False, choices=UNLISTED)
    pub_date = models.DateTimeField('date posted', auto_now_add=True, blank=True)
    visibility = models.CharField(max_length=10, default = 'PUBL', choices=POST_VISIBILITY)
    
    def __str__(self):
        return super().__str__() + "    ---------   " + self.title

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date posted', auto_now_add=True, blank=True)
