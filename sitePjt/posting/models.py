from django.db import models
from accounts.models import Author
import uuid
from django.conf import settings
POST_VISIBILITY = (
    ('PUBLIC', 'Public'),
    ('PRIVATE', 'Prviate to self'),
    ('FRIENDS', 'Private to friends'),
    ('FOAF', 'Private to friends of friends'),
    ('SERVERONLY', 'Private to local friends'),
)
CONTENT_TYPE = {
    ('text/plain', 'Plain text'),
    ('text/markdown', 'Markdown'),
    ('image/png;base64', 'Image/png'),
    ('image/jpeg;base64', 'Image/jpeg'),
    ('application/base64', 'Application'),
}
CONTENT_TYPE_COMMENT = {
    ('text/plain', 'Plain Text'),
    ('text/markdown', 'Markdown'),
}

UNLISTED = {
    (True, 'True'),
    (False, 'False'),
}

'''
    namely a Post model, belong to author
'''
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, max_length=50, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    contentType = models.CharField(max_length=20, default = 'text/plain', choices=CONTENT_TYPE)
    #TODO: Update origin url
    origin = models.CharField(default="",max_length=200, editable=False)
    source = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    categories = models.CharField(max_length=200, blank=True)
    unlisted = models.BooleanField(default=False, choices=UNLISTED)
    published = models.DateTimeField('date posted', auto_now_add=True, blank=True)
    visibility = models.CharField(max_length=10, default = 'PUBLIC', choices=POST_VISIBILITY)
    visibleTo = models.TextField(blank=True)
    #visibleTo: field: array of author

    def __str__(self):
        return super().__str__() + "    ------      " +self.title

'''
    namely a Comment model, belong to author and post
'''    
class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    contentType = models.CharField(max_length=20, default = 'text/plain', choices=CONTENT_TYPE_COMMENT)
    comment = models.CharField(max_length=200)
    published = models.DateTimeField('date posted', auto_now_add=True, blank=True)

