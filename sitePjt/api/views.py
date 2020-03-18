from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.parsers import JSONParser
from django.contrib.auth import get_user_model
from django.db.models import Q
import json
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed, HttpResponseForbidden
from posting.models import Post, Comment
from friendship.models import Friendship, FriendRequest,Friend
from posting.forms import CommentForm
from friendship import views as FriendshipViews
from .serializers import PostSerializer, AuthorSerializer, PostListSerializer, CommentSerializer, CommentListSerializer, FriendshipSerializer
Author = get_user_model()

@api_view(['GET'])
def view_public_post(request):
    if request.method == 'GET':
        try:
            posts = Post.objects.filter(
                visibility='PUBLIC', unlisted=False).order_by('-published')
            count = len(posts)
            serializer = PostListSerializer(
                posts, context={'query': 'posts', 'count': count})
            return Response(serializer.data)
        except Exception as e:
            print(e)
        return HttpResponseNotFound()
    return HttpResponseBadRequest()


@api_view(['GET', 'POST'])
def handle_auth_posts(request):
    if request.method == 'GET':
        try:
            posts = getVisiblePosts(request.user)
            count = len(posts)
            serializer = PostListSerializer(
                posts, context={'query': 'posts', 'count': count})
            return Response(serializer.data)
        except Exception as e:
            print(e)
        return HttpResponseNotFound()
    elif request.method == 'POST':
        try:
            context = {
                "query": "addPost",
                "success": None,
                "message": None,
            }
            if not request.user.is_anonymous:
                data = request.body
                post = json.loads(data)
                post_form = post.get('post_form')
                #post_form['author'] = request.user
                #print(post_form)
            
                serializer = PostSerializer(data=post_form, context = {'author': request.user})
                if serializer.is_valid():
                    serializer.save()
                    context['success'] = True
                    context['message'] = "New Post Added"
                    return Response(context, status=200)
                else:
                    print(serializer.errors)
                    context['success'] = False
                    context['message'] = "Invalid form data"
                    return Response(context, status=403)
            else:
                context['success'] = False
                context['message'] = "Login First!"
                return Response(context, status=403)

        except Exception as e:
            print(e)
            return HttpResponseServerError()
    else:
        return HttpResponseBadRequest()


@api_view(['GET'])
def view_author_posts(request, author_id):
    if request.method == 'GET':
        try:
            author = Author.objects.get(id=author_id)
            posts = getVisiblePosts(request.user, author)
            count = len(posts)
            serializer = PostListSerializer(
                posts, context={'query': 'posts', 'count': count})
            return Response(serializer.data)
        except Exception as e:
            print(e)
        return HttpResponseNotFound()
    return HttpResponseBadRequest()


@api_view(['GET'])
def view_single_post(request, post_id):
    if request.method == 'GET':
        try:
            post = Post.objects.get(id=post_id)
            if checkVisibility(request.user, post):
                serializer = PostSerializer(post)
                return Response(serializer.data)
            else:
                return Response(b"You dont have visibility to this post.", status=403)
        except Exception as e:
            print(e)
        return HttpResponseNotFound()
    return HttpResponseBadRequest()


@api_view(['GET', 'POST'])
def handle_comments(request, post_id):
    if request.method == 'GET':
        try:
            post = Post.objects.get(id=post_id)
            if request.user.is_anonymous or not checkVisibility(request.user, post):
                return HttpResponseForbidden(b"You dont have visibility.")
            comments = Comment.objects.filter(post=post)
            count = len(comments)
            serializer = CommentListSerializer(
                comments, context={'query': 'comments', 'count': count})
            return Response(serializer.data)
        except Exception as e:
            print(e)
        return HttpResponseNotFound()

    elif request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id)
            context = {
                "query": "addComment",
                "success": None,
                "message": None,
            }
            if not request.user.is_anonymous and checkVisibility(request.user, post):
                #Check Visibility
                data = request.body
                body = json.loads(data)
                content = body['comment']
                contentType = body['contentType']
                comment = Comment(post=post, author=request.user,
                                comment=content, contentType=contentType)
                comment.save()
                context['success'] = True
                context['message'] = "Comment Added"
                return Response(context, status=200)
            else:
                context['success'] = False
                context['message'] = "Comment not Allowed"
                return Response(context, status=403)
        except Exception as e:
            print(e)
            return HttpResponseServerError()
    else:
        return HttpResponseBadRequest()


@api_view(['GET', 'POST'])
def ViewProfile(request, author_id):
    if request.method == 'GET':
        try:
            author = Author.objects.filter(id=author_id)
            if author.exists():
                serializer = AuthorSerializer(author[0])
                return Response(serializer.data)
            else:
                return HttpResponseNotFound(b"User Not found")

        except Exception as e:
            print(e)

    elif request.method == 'POST':
        #check user authenticaiton first
        if request.user.is_anonymous or (author_id != request.user.id):
            return Response(b"Authentication required!", status=403)
        try:
            if author_id:
                author = Author.objects.filter(id=author_id)
                if author.exists():
                    serializer = AuthorSerializer(author[0], data=request.POST, partial=True)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response(serializer.data)
            return Response(b"invalid author form data", status=403)
        except Exception as e:
            print(e)
            return HttpResponseServerError()
    else:
        return HttpResponseNotAllowed()


@api_view(['GET'])
def ViewComment(request, post_id):

    if request.method == 'GET':
        try:
            post = Post.objects.get(id=post_id)
            if post:
                serializer = PostSerializer(post)
                return Response(serializer.data)
            else:
                return HttpResponseNotFound(b"User Not found")
        except Exception as e:
            print(e)
            return HttpResponseServerError()
    else:
        return HttpResponseBadRequest()


@api_view(['GET', 'POST'])
def get_friendlist(request, author_id):
    if request.method == 'GET':
        try:
            friend = Friend.objects.filter(friend_id=author_id)
            result = []
            if friend.exists():
                friendships = Friendship.objects.filter(Q(author_a=friend[0]) | Q(author_b=friend[0]))
                for friendship in friendships:
                    if friendship.author_a.friend_id == author_id:
                        result.append(friendship.author_b.friend_url)
                    else:
                        result.append(friendship.author_a.friend_url)
                
            serializer = FriendshipSerializer(result, exclude=['author'])
            return Response(serializer.data)
        except Exception as e:
            print(e)
            return HttpResponseServerError()
    elif request.method == 'POST':
        try:
            body = json.loads(request.body)
            authors = body['authors']
            author = Friend.objects.get(friend_id=author_id)
            friendIDList = []
            for friend_id in authors:
                friend = Friend.objects.get(friend_id=friend_id)
                if FriendshipViews.checkFriendship(author.friend_id, friend_id):
                    friendIDList.append(friend.friend_url)
            serializer = FriendshipSerializer(
                friendIDList, context={'author': author_url})
            return Response(serializer.data)
        except Exception as e:
            print(e)
            return HttpResponseServerError()

    else:
        return HttpResponseBadRequest()


@api_view(['GET'])
def check_friendship(request, author1_id, author2_id):
    if request.method == 'GET':
        try:
            context = {
                'query': 'friends',
                'friends': None,
                'authors': []
            }
            context['authors'].append(author1_id)
            context['authors'].append(author2_id)
            if FriendshipViews.checkFriendship(author1_id, author2_id):
                context['friends'] = True
                return Response(context, status=200)
            else:
                context['friends'] = False
                return Response(context, status=200)
        except Exception as e:
            print(e)
            return HttpResponseServerError()
    else:
        return HttpResponseBadRequest()


@api_view(['POST'])
def make_friendRequest(request):
    if request.method == 'POST':
        if request.user.is_anonymous:
            return HttpResponseForbidden("Login required!")
        try:
            context = {
                'query': 'friends',
                'success': None,
                'authors': []
            }
            # Get a friend in Frien table
            body = json.loads(request.body)
            author = body['author']
            friend = body['friend']
            if request.user.id != author['friend_id']:
                return HttpResponseForbidden("Authentication failed!")
            author_from, created_from = Friend.objects.get_or_create(**author)
            author_to, created_to = Friend.objects.get_or_create(**friend)
            context['authors'].append(author_from.friend_id)
            context['authors'].append(author_to.friend_id)

            #Create a new friend request if authors are not friend and no such friend request exists
            friendship = FriendshipViews.checkFriendship(author_from.friend_id, author_to.friend_id)
            if not friendship:
                try:
                    oppsite_req =  FriendRequest.objects.get(author_from=author_to, author_to=author_from)
                    oppsite_req.delete()
                    #become friends automatically
                    if author_from.friend_id < author_to.friend_id:
                        a, b = author_from, author_to
                    else:
                        b, a = author_from, author_to
                    Friendship.objects.create(author_a=a, author_b=b)
                    context['success'] = True
                    return Response(context, status=200)
                except Exception as e:
                    request, created = FriendRequest.objects.get_or_create(author_from=author_from, author_to=author_to)
                

            request = FriendRequest.objects.filter(author_from=author_from, author_to=author_to)

            if request:
                context['success'] = True
                return Response(context, status=200)
            else:
                context['success'] = False
                return Response(context, status=200)

        except Exception as e:
            print(e)
            return HttpResponseServerError()
    else:
        return HttpResponseBadRequest()

#helper funciton
def getVisiblePosts(requester, author=None):
    result = []
    if requester.is_anonymous:
        if author:
            return Post.objects.filter(author=author, visibility='PUBLIC', unlisted=False).order_by('-published')
        else:
            return Post.objects.filter(visibility='PUBLIC', unlisted=False).order_by('-published')

    if author:
        posts = Post.objects.filter(
            author=author, unlisted=False).order_by('-published')
    else:
        posts = Post.objects.filter(unlisted=False).order_by('-published')

    for post in posts:
        if post.author == requester:
            result.append(post)
        elif post.visibility == 'PUBLIC':
            result.append(post)
        elif post.visibility == 'FRIENDS':
            if FriendshipViews.checkFriendship(post.author.id, requester.id):
                result.append(post)
        elif post.visibility == 'FOAF':
            if FriendshipViews.checkFriendship(post.author.id, requester.id):
                result.append(post)
            else:
                for friend in FriendshipViews.getAllFriends(post.author.id):
                    if FriendshipViews.checkFriendship(friend.id, requester.id):
                        result.append(post)
        elif post.visibility == 'SERVERONLY':
            if post.author.host == requester.host:
                result.append(post)
            print("SERVERONLY unimplemented.")
        #if request.user.id in post.visibleTo and (not post in post_list):
            #post_list.append(post)
    return result

#Return a boolean representing the visibility of input post to requester


def checkVisibility(requester, post):
    if post.author == requester or post.visibility == 'PUBLIC':
        return True
    else:
        req_friendsList = FriendshipViews.getAllFriends(requester.id)
        if post.visibility == 'FRIENDS':
            if post.author in req_friendsList:
                return True
        elif post.visibility == 'FOAF':
            #Case1: author and requester are friends => return True
            if post.author in req_friendsList:
                return True
            #Case2: author and a friend of requester are friends => return True
            else:
                for friend in req_friendsList:
                    if FriendshipViews.checkFriendship(friend.id, post.id):
                        return True

        elif post.visibility == 'SERVERONLY':
            print("SERVERONLY unimplemented.But I give you visibility by this time.")
            if post.author.host == requester.host:
                return True
    #if request.user.id in post.visibleTo and (not post in post_list):
        #post_list.append(post)
    return False
