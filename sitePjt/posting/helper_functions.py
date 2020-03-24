from friendship.helper_functions import checkFriendship, getAllFriends
from django.db.models.functions import Cast
import datetime
from django.db.models import DateTimeField
from .models import Post, Comment
from accounts.models import Author
import requests
from requests.auth import HTTPBasicAuth
from .serializers import AuthorSerializer, PostSerializer, CommentSerializer, PostListSerializer, PostCreateSerializer
from django.utils.dateparse import parse_datetime

#helper funciton
'''
    get all visible posts, depends on the state of current user

    POST_VISIBILITY = (
    ('PUBLIC', 'Public'),
    ('PRIVATE', 'Prviate to self'),
    ('FRIENDS', 'Private to friends'),
    ('FOAF', 'Private to friends of friends'),
    ('SERVERONLY', 'Private to local friends'),
    )

'''

def getVisiblePosts(requester, author=None):
    result = []
    #the current user hasn't login yet, show some random public posts
    if requester.is_anonymous:
        if author:
            return Post.objects.filter(author=author, visibility='PUBLIC', unlisted=False).order_by('-published')
        else:
            return Post.objects.filter(visibility='PUBLIC', unlisted=False).order_by('-published')

    #only check one author's posts or all posts
    if author:
        posts = Post.objects.filter(author=author, unlisted=False).order_by('-published')
    else:
        posts = Post.objects.filter(unlisted=False).order_by('-published')

    for post in posts:
        if post.author == requester:  # my post
            result.append(post)
        elif post.visibility == 'PUBLIC':  # everyone can see's post
            result.append(post)
        elif post.visibility == 'FRIENDS':  # if friends then append this post
            if checkFriendship(post.author.id, requester.id):
                result.append(post)
        elif post.visibility == 'FOAF':  # friends of friends also can see
            if checkFriendship(post.author.id, requester.id):
                result.append(post)
            else:
                for friend in getAllFriends(post.author.id):
                    if checkFriendship(friend.friend_id, requester.id):
                        result.append(post)
        elif post.visibility == 'SERVERONLY':  # requires to be local friends
            if post.author.host == requester.host:
                result.append(post)
            print("SERVERONLY unimplemented.")
    if author == requester:
        unlisted_posts = Post.objects.filter(author=author, unlisted=True)
        for post in unlisted_posts:
            result.append(post)

    return result

def getNodePublicPosts(Node=None, user=None):
    user = '5000@remote.com'
    pwd = '1'
    #Try request from remote server
    #TODO:headers={"content-type":request.user.id}
    response = requests.get(' http://127.0.0.1:5000/service/posts/', auth=(user, pwd))
    #TODO:Error Handle
    remote_posts = []
    if response.status_code == 200:
        remote_public_posts =response.json()       
        for item in remote_public_posts['posts']:
            #Get 
            #everything is a string up to here
            '''   
            serializer = PostCreateSerializer(data=item, context=item)
            if serializer.is_valid():
                remote_posts.append(Post(**serializer.data))
            '''
            author = Author(**item.get('author'))
            author.id = findAuthorIdFromUrl(item.get('author')['url'])
            published = parse_datetime(item['published'])
            post = PostSerializer(data=item)
            if post.is_valid():
                #print(post.validated_data)
                post = Post(**post.validated_data)
                post.id = item['id']
                post.published = published
                post.author = author
                remote_posts.append(post)  
             
    return remote_posts
def getNodePostComment(post_id,Node=None):
    user = '5000@remote.com'
    pwd = '1'
    #Try request from remote server
    url = 'http://127.0.0.1:5000/service/posts/{}/comments/'.format(str(post_id))
    response = requests.get(url, auth=(user, pwd))
    #TODO: Error Handle
    remote_comments = []
    if response.status_code == 200:
        remote_comments_data = response.json()
        for item in remote_comments_data['comments']:
            author = Author(**item.get('author'))
            #author.id = findAuthorIdFromUrl(item.get('author')['url'])
            published = parse_datetime(item['published'])
            comment = CommentSerializer(data=item)
            if comment.is_valid():
                comment = Comment(**comment.validated_data)
                comment.id = item['id']
                comment.published = published
                comment.author = author
                remote_comments.append(comment)
    return remote_comments  

def getNodePost(post_id,Node=None):
    user = '5000@remote.com'
    pwd = '1'
    #Try request from remote server
    url = 'http://127.0.0.1:5000/service/posts/{}/'.format(str(post_id))
    response = requests.get(url, auth=(user, pwd))
    #TODO: Error Handle
    post = None
    if response.status_code == 200:  
        remote_post =response.json()
        author = Author(**remote_post.get('author'))
        author.id = findAuthorIdFromUrl(remote_post.get('author')['url'])
        published = parse_datetime(remote_post['published'])
        post = PostSerializer(data=remote_post)
        if post.is_valid():
            post = Post(**post.validated_data)
            post.id = remote_post['id']
            post.published = published
            post.author = author
    return post

def postNodePostComment(post_id,comment_data,Node=None):
    user = '5000@remote.com'
    pwd = '1'
    #Try request from remote server
    url = 'http://127.0.0.1:5000/service/posts/{}/comments/'.format(str(post_id))
    comment = CommentSerializer(instance=comment_data)
    response = requests.get(url, auth=(user, pwd))


#TODO: Not Finish Yet, Waiting for friendship
def getNodeAuthorPosts(author_id,Node=None):
    user = '5000@remote.com'
    pwd = '1'
    #Try request from remote server
    url = 'http://127.0.0.1:5000/service/author/{}/posts/'.format(str(author_id))
    response = requests.get(url, auth=(user, pwd))
    authorPosts = None
    if response.status_code == 200:
        remote_author_posts = response.json()
        print(remote_author_posts)  

def findAuthorIdFromUrl(url):
    idx = url[:-1].rindex('/')
    return url[idx+1:-1]