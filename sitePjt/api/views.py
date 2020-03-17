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
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseServerError
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
@login_required
def handle_comments(request, post_id):
    if request.method == 'GET':
        try:
            post = Post.objects.get(id=post_id)
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
            if checkVisibility(request.user, post):
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
    return HttpResponseBadRequest()


@api_view(['GET', 'POST'])
def ViewProfile(request, author_id):
    if request.method == 'GET':
        try:
            author = Author.objects.get(id=author_id)
            if author:
                serializer = AuthorSerializer(author)
                return Response(serializer.data)
            else:
                return HttpResponseNotFound(b"User Not found")
        except Exception as e:
            print(e)

    return HttpResponseBadRequest()

    if request.method == 'POST':
        #check user authenticaiton first
        if request.user.is_anonymous or (author_id != request.user.id):
            return Response(b"Authentication required!", status=403)
        try:
            if author_id:
                author = Author.objects.get(id=author_id)
                serializer = AuthorSerializer(
                    author, data=request.POST, partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(serializer.data)
        except Exception as e:
            print(e)
            return Response(e)

    return HttpResponseBadRequest()


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
            author = Author.objects.get(id=author_id)
            friendships = Friendship.objects.filter(Q(author_a=author) | Q(author_b=author))
            result = []
            for friendship in friendships:
                if friendship.author_a == author:
                    result.append(friendship.author_b.id)
                else:
                    result.append(friendship.author_a.id)
            if result:
                serializer = FriendshipSerializer(result, exclude=['author'])
                return Response(serializer.data)
            else:
                return HttpResponseNotFound(b"User Not found")
        except Exception as e:
            print(e)
            return HttpResponseServerError()
    elif request.method == 'POST':
        try:
            data = request.body
            body = json.loads(data)
            authors = body['authors']
            print(authors)
            friendIDList = []
            if data:
                for friend_id in authors:
                    if FriendshipViews.checkFriendship(author_id, friend_id):
                        friendIDList.append(friend_id)
                serializer = FriendshipSerializer(
                    friendIDList, context={'author': author_id})
                return Response(serializer.data)
            else:
                return Response(b"Invalid json file", status=403)
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
            friend1 = Friend.objects.get(friend_id=author1_id) #Get a friend in Frien table
            friend2 = Friend.objects.get(friend_id=author2_id)
            if friend1 and friend2:
                if FriendshipViews.checkFriendship(friend1, friend2):
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
        try:
            context = {
                'query': 'friends',
                'success': None,
                'authors': []
            }
            # Get a friend in Frien table
            data = request.body
            body = json.loads(data)
            author = body['author']
            friend = body['friend']
            author_from, created_from = Friend.objects.get_or_create(**author)
            author_to, created_to = Friend.objects.get_or_create(**friend)
            context['authors'].append(author_from.friend_id)
            context['authors'].append(author_to.friend_id)

            #Create a new friend request if authors are not friend and no such friend request exists
            if not FriendshipViews.checkFriendship(author_from, author_to):
                request = FriendRequest.objects.get_or_create(author_from=author_from, author_to=author_to)

            request = FriendRequest.objects.filter(author_from=author_from, author_to=author_to)
            if request:
                context['success'] = True
                return Response(context, status=200)
            else:
                return Response(b"Invalid authors info", status=403)

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


'''
@api_view(['GET', 'POST'])
def post_list(request):
    if request.method == 'GET':
        data = Post.objects.all()
        serializer = PostSerializer(
            data, context={'request': request}, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['PUT', 'DELETE'])
def post_detail(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        serializer = PostSerializer(
            post, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
'''

'''
class ListUsers(APIView):
    """
    View to list all users in the system.
    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        usernames = [user.username for user in User.objects.all()]
        return Response(usernames)
'''
