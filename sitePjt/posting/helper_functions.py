from friendship.helper_functions import checkFriendship, getAllFriends
from django.db.models.functions import Cast
import datetime
from django.db.models import DateTimeField
from .models import Post, Comment
from accounts.models import ServerNode
from accounts.models import Author, ServerNode
import requests
from requests.auth import HTTPBasicAuth
from .serializers import AuthorSerializer, PostSerializer, CommentSerializer, PostListSerializer, PostCreateSerializer
from django.utils.dateparse import parse_datetime
from django.core import serializers
from django.conf import settings
import json
from django.utils import timezone
from django.db.models import Q


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
    if requester.is_anonymous or requester.host != settings.HOSTNAME:
        if author:
            return list(Post.objects.filter(author=author, visibility='PUBLIC', unlisted=False).order_by('-published'))
        else:
            return list(Post.objects.filter(visibility='PUBLIC', unlisted=False).order_by('-published'))

    #only check one author's posts or all posts
    remote_visibile_posts = []
    if author:
        #Get all remote visibile post of author
        node = ServerNode.objects.filter(host_url=author.host+'service/')
        node = node[0] if node.exists() else None
        if node:
            remote_visibile_posts = getRemoteAuthorPosts(
                author.id, requester.id, node)
        local_posts = Post.objects.filter(
            author=author, unlisted=False).order_by('-published')
    else:
        #Get all remote visibile post
        nodes = ServerNode.objects.all()
        remote_visibile_posts = getRemoteVisiblePost(nodes, requester.id)
        local_posts = Post.objects.filter(
            unlisted=False).order_by('-published')
    #Get all local visibile post
    for post in local_posts:
        if post.author == requester:  # my post
            result.append(post)
        elif post.visibility == 'PUBLIC':  # everyone can see's post
            result.append(post)
        elif post.visibility == 'FRIENDS':  # if friends then append this post
            if checkFriendship(post.author.id, requester.id):
                result.append(post)
        elif post.visibility == 'FOAF':  # friends of friends also can see
            #Check it requester is friend of author or not.
            if checkFriendship(post.author.id, requester.id):
                result.append(post)
            else:
            #Check it requester is FOAF of author or not.
                for friend in getAllFriends(post.author.id):
                    if checkFriendship(friend.friend_id, requester.id):
                        result.append(post)
        elif post.visibility == 'SERVERONLY':  # requires to be local friends
            if post.author.host == requester.host:
                result.append(post)
    if author == requester:
        unlisted_posts = Post.objects.filter(author=author, unlisted=True)
        for post in unlisted_posts:
            result.append(post)

    result += remote_visibile_posts
    return result


def getRemotePublicPosts():
    remote_posts = []
    nodes = ServerNode.objects.all()

    if not nodes.exists():
        return remote_posts
    for node in nodes:
        url = "{}posts".format(node.host_url)
        auth = (node.server_username, node.server_password)
        try:
            response = requests.get(url, auth=auth,timeout=5)
            if response.status_code == 200:
                response = response.json()
                remote_public_posts = response['posts']
                for item in remote_public_posts:
                    author = getJsonDecodeAuthor(item['author'])
                    post = getJsonDecodePost(item)
                    post.author = author
                    remote_posts.append(post)
            else:
                print(response.json())
                break
        except Exception as e:
            #print(e)
            pass


    return remote_posts


def getRemoteVisiblePost(nodes, requester_id):
    posts = []
    for node in nodes:
        url = '{}author/posts'.format(node.host_url)
        auth = (node.server_username, node.server_password)
        headers = {'X-USER-ID': requester_id}
        try:
            response = requests.get(url, auth=auth, headers=headers,timeout=5)
            if response.status_code == 200:
                response = response.json()
                remote_posts = response['posts']
                for item in remote_posts:
                    post = getJsonDecodePost(item)
                    post.author = getJsonDecodeAuthor(item['author'])
                    posts.append(post)
            else:
                print(response.json())
                break
        except Exception as e:
            #print(e)
            pass

        
    return posts


def getRemotePost(post_id, nodes, requester_id):
    post = None
    for node in nodes:
        url = '{}posts/{}'.format(node.host_url, str(post_id))
        auth = (node.server_username, node.server_password)
        headers = {'X-USER-ID': requester_id}
        response = None 
        try:
            response = requests.get(url, auth=auth, headers=headers,timeout=5)
            if response.status_code == 200:
                response = response.json()
                remote_post = response['post']
                post = getJsonDecodePost(remote_post)
                post.author = getJsonDecodeAuthor(remote_post['author'])
                break
            else:
                print(response.json())
                break
        except Exception as e:
            #print(e)
            pass
    return post


def getRemotePostComment(post, requester_id):
    remote_comments = []
    '''
    #TODO add field host of node
    post_host = post.author.host + ""
    node = ServerNode.objects.filter(host=)
    '''
    for node in ServerNode.objects.all():
        url = '{}posts/{}/comments'.format(node.host_url, post.id)
        auth = (node.server_username, node.server_password)
        headers = {'X-USER-ID': requester_id}
        try:
            response = requests.get(url, auth=auth, headers=headers,timeout=5)
            if response.status_code == 200:
                response = response.json()
                for item in response['comments']:
                    remote_comments.append(getJsonDecodeComment(item))
                break
            else:
                print(response.json())
                break
        except Exception as e:
            #print(e)
            pass

    return remote_comments

def postRemotePostComment(comment_data, requester_id):
    author = {
        'id': comment_data.author.url,
        'host': comment_data.author.host,
        'displayName': comment_data.author.displayName,
        'url': comment_data.author.url,
        'github': comment_data.author.github,
    }
    comment = {
        'author': author,
        'comment': comment_data.comment,
        'contentType': comment_data.contentType,
        'published': str(timezone.now()),
        'id': str(comment_data.id)
    }
    body = {
        'query': 'addComment',
        'post': comment_data.post.origin,
        'comment': comment
    }
    #response = requests.get(url, auth=(user, pwd))
    nodes = ServerNode.objects.all()
    for node in nodes:
        auth = (node.server_username, node.server_password)
        headers = {'X-USER-ID': requester_id}
        post_id = body['post'].split('/')[-2]
        url = '{}posts/{}/comments'.format(node.host_url, str(post_id))
        try:
            response = requests.post(url, json=body, auth=auth, headers=headers,timeout=5)
            if response.status_code == 200:
                break
            else:
                print(response.json())
                break
        except Exception as e:
            #print(e)
            pass

def getRemoteAuthorPosts(author_id, requester_id, node):
    remote_author_posts = []
    if not node:
        return remote_author_posts
    url = '{}author/{}/posts'.format(node.host_url, author_id)
    auth = (node.server_username, node.server_password)
    headers = {'X-USER-ID': requester_id}
    try:
        response = requests.get(url, auth=auth, headers=headers )
        if response.status_code == 200:
            response = response.json()
            remote_posts = response['posts']
            for item in remote_posts:
                post = getJsonDecodePost(item)
                post.author = getJsonDecodeAuthor(item['author'])
                remote_author_posts.append(post)
        else:
            print(response.json())
    except Exception as e:
        #print(e)
        pass

    return remote_author_posts


def findAuthorIdFromUrl(url):
    if '/' not in url:
        return url
    elif url[-1] == '/':
        idx = url[:-1].rindex('/')
        return url[idx+1:-1]
    else:
        idx = url.rindex('/')
        return url[idx+1:]


def getJsonDecodeAuthor(remote_author):
    author = Author()
    author.id = findAuthorIdFromUrl(remote_author['url'])
    author.url = remote_author['url'] if 'url' in remote_author.keys(
    ) else 'None'
    author.displayName = remote_author['displayName'] if 'displayName' in remote_author.keys(
    ) else 'None'
    author.bio = remote_author['bio'] if 'bio' in remote_author.keys(
    ) else 'None'
    author.host = remote_author['host'] if 'host' in remote_author.keys(
    ) else 'None'
    author.github = remote_author['github'] if 'github' in remote_author.keys(
    ) else 'None'
    author.date_joined = remote_author['date_joined'] if 'date_joined' in remote_author.keys(
    ) else 'None'
    author.last_login = remote_author['last_login'] if 'last_login' in remote_author.keys(
    ) else 'None'
    return author


def getJsonDecodeComment(remote_comment):
    comment = Comment()
    comment.comment = remote_comment['comment'] if 'comment' in remote_comment.keys(
    ) else 'None'
    comment.author = getJsonDecodeAuthor(
        remote_comment['author']) if 'author' in remote_comment.keys() else 'None'
    comment.id = remote_comment['id'] if 'id' in remote_comment.keys(
    ) else 'None'
    comment.contentType = remote_comment['contentType'] if 'contentType' in remote_comment.keys(
    ) else 'None'
    comment.published = parse_datetime(
        remote_comment['published']) if 'published' in remote_comment.keys() else 'None'
    return comment


def getJsonDecodePost(remote_post):
    post = Post()
    post.title = remote_post['title'] if 'title' in remote_post.keys(
    ) else 'None'
    post.source = remote_post['source'] if 'source' in remote_post.keys(
    ) else 'None'
    post.origin = remote_post['origin'] if 'origin' in remote_post.keys(
    ) else 'None'
    post.contentType = remote_post['contentType'] if 'contentType' in remote_post.keys(
    ) else 'None'
    post.content = remote_post['content'] if 'content' in remote_post.keys(
    ) else 'None'
    post.categories = "#" + "#".join(remote_post['categories']) if 'categories' in remote_post.keys(
    ) else 'None'
    post.published = parse_datetime(
        remote_post['published']) if 'published' in remote_post.keys() else 'None'
    post.id = remote_post['id'] if 'id' in remote_post.keys() else 'None'
    post.visibility = remote_post['visibility'] if 'visibility' in remote_post.keys(
    ) else 'None'
    post.unlisted = remote_post['unlisted'] if 'count' in remote_post.keys(
    ) else 'None'
    #post.count=remote_post['count'] if 'count' in remote_post.keys() else 'None'
    #post.size=remote_post['size'] if 'size' in remote_post.keys() else 'None'
    #post.next=remote_post['next'] if 'next' in remote_post.keys() else 'None'
    #post.description=remote_post['description'] if 'description' in remote_post.keys() else 'None'
    return post
    #TODO:visibleTo
