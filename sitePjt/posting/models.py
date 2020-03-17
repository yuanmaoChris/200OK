from django.db import models
from accounts.models import Author
import uuid

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

'''
    namely a Post model, belong to author
'''
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    contentType = models.CharField(max_length=4, default = 'text', choices=CONTENT_TYPE)
    description = models.CharField(max_length=50, blank=True)
    origin = models.CharField(max_length=50, blank=True)
    source = models.CharField(max_length=50, blank=True)
    content = models.CharField(max_length=200)
    categories = models.CharField(max_length=200, blank=True)
    unlisted = models.BooleanField(default=False, choices=UNLISTED)
    published = models.DateTimeField('date posted', auto_now_add=True, blank=True)
    visibility = models.CharField(max_length=10, default = 'PUBLIC', choices=POST_VISIBILITY)

    def __str__(self):
        return super().__str__() + "    ------      " +self.title
'''
    namely a Comment model, belong to author and post
'''    
class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    contentType = models.CharField(max_length=4, default = 'text', choices=CONTENT_TYPE)
    comment = models.CharField(max_length=200)
    published = models.DateTimeField('date posted', auto_now_add=True, blank=True)
