from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.parsers import JSONParser
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings
import json
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed, HttpResponseForbidden
from posting.models import Post, Comment
from friendship.models import Friendship, FriendRequest,Friend
from posting.forms import CommentForm
from friendship.helper_functions import checkFriendship, getAllFriends
from .serializers import PostSerializer, AuthorSerializer, CommentSerializer, FriendshipSerializer
from .permissions import IsAuthenticatedAndNode
from .pagination import CustomPagination

Author = get_user_model()

def findAuthorIdFromUrl(url):
    if '/' not in url:
        return url
    elif url[-1] == '/':
        idx = url[:-1].rindex('/')
        return url[idx+1:-1]
    else:
        idx = url.rindex('/')
        return url[idx+1:]

@api_view(['GET'])
@permission_classes([IsAuthenticatedAndNode])
def view_public_post(request):
    '''
        GET: To get all public posts 
    '''
    if request.method == 'GET':
        try:
            paginator = CustomPagination()
            posts = Post.objects.filter(visibility='PUBLIC', unlisted=False).order_by('-published')
            try:
                posts = paginator.paginate_queryset(posts, request)
            except Exception as e:
                return HttpResponseNotFound(e)
            serializer = PostSerializer(posts, many=True)
            response = paginator.get_paginated_response('posts', 'posts', serializer.data)
            return response
        except Exception as e:
            print(e)
            return HttpResponseServerError(e)
    else:
        #method not allowed
        return HttpResponseNotAllowed()

#TODO: AUTHOR INFO
@api_view(['GET'])
@permission_classes([IsAuthenticatedAndNode])
def handle_auth_posts(request):
    '''
        GET:To get posts with authenticated requester
        POST: To add a post with authenticated requester
    '''
    #Handle GET requests
    if request.method == 'GET':
        try:
            #Parse post information from request
            data = json.loads(request.body)
            '''
            if not 'requester' in data.key():
                return HttpResponseForbidden("Who's requesting posts? Put author info in JSON body under 'requester'")
            requster, _ = Author.objects.get_or_create(**post['requester'])
            '''
            #Get all posts that current authenticated user has visitbility of
            posts = getVisiblePosts(request.user) 
            paginator = CustomPagination()
            try:
                posts = paginator.paginate_queryset(posts, request)
            except Exception as e:
                return HttpResponseNotFound(e)
            serializer = PostSerializer(posts, many=True)
            response = paginator.get_paginated_response('posts', 'posts', serializer.data)
            return response
            return Response(serializer.data)
        except Exception as e:
            return HttpResponseServerError(e)

    #Method not allowed
    else:
        return HttpResponseNotAllowed()
    '''
    #Handle POST requests
    elif request.method == 'POST':
        try:
            #Initialize response context
            context = {
                "query": "addPost",
                "success": None,
                "message": None,
            }
            #Parse requester information from request
            data = json.loads(request.body)
            #Make a new post
            #Parse post information from request
            post_form = data.get('post_form')
            
            serializer = PostSerializer(data=post_form, context = {'author': requester})
            #post information data is valid -> save post to database and return success response
            if serializer.is_valid():
                newpost = serializer.save()
                newpost.origin = "{}/posts/{}/".format(settings.HOSTNAME, newpost.id)
                context['success'] = True
                context['message'] = "New Post Added"
                return Response(context, status=200)
            #post information data is invalid -> return failure response
            else:
                print(serializer.errors)
                context['success'] = False
                context['message'] = "Invalid form data"
                return Response(context, status=403)

        #Server error when handling request
        except Exception as e:
            return HttpResponseServerError(e)
        '''
#TODO: get_or_create
@api_view(['GET'])
@permission_classes([IsAuthenticatedAndNode])
def view_author_posts(request, author_id):
    '''
       G To get all visiable posts by given author
    '''    
    #Handle GET request
    if request.method == 'GET':
        try:
            #Get author instance whose posts to view
            author = Author.objects.filter(id=author_id)
            if not author.exsits():
                return HttpResponseNotFound("Author Profile Not Found.")
            author = Author.objects.get(id=author_id)
            #filter out all posts that requester does not have visibility of
            posts = getVisiblePosts(request.user, author)
            paginator = CustomPagination()
            try:
                posts = paginator.paginate_queryset(posts, request)
            except Exception as e:
                return HttpResponseNotFound(e)
            serializer = PostSerializer(posts, many=True)
            response = paginator.get_paginated_response('posts', 'posts', serializer.data)
            return response
            
        #Server error when handling request
        except Exception as e:
            return HttpResponseServerError(e)
    #Method not allowed       
    return HttpResponseNotAllowed()

#TODO: get_or_create
@api_view(['GET'])
@permission_classes([IsAuthenticatedAndNode])
def view_single_post(request, post_id):
    '''
        GET: To get a single visiable post by given post id 
    '''
    if request.method == 'GET':
        try:
            #Get the post specified by request
            post = Post.objects.filter(id=post_id)
            if not post.exists():
                return HttpResponseNotFound("Post Not Found.")
            post = Post.objects.get(id=post_id)

            #Case 1: User has visibility
            if checkVisibility(request.user, post):
                serializer = PostSerializer(post)
                response = {}
                response['query'] = 'posts'
                #response['count'] = 1
                response['post'] = serializer.data
                return Response(response)
                #serializer = PostSerializer(post)
                #return Response(serializer.data)
                
            #Case 2: User does not have visibility
            else:
                return HttpResponseForbidden(b"You dont have visibility to this post.")
        #Server error when handling request  
        except Exception as e:
            return HttpResponseServerError(e)

    #Ask for a FOAF post 
    if request.method == 'POST':
        try:
            #Parse data from request
            data = json.loads(request.body)

            #Validate data
            if not ('postid' in data.keys() and 'url' in  data.keys() and 'author' in data.keys() and 'friends' in data.keys()):
                return Response("Invalid request data", status=403)
            
            #Get the post specified by request
            post = Post.objects.filter(id=data['postid'])
            if not post.exists():
                return HttpResponseNotFound("Post Not Found.")
            post = post[0]
            if not post.visibility == "FOAF":
                return HttpResponseForbidden("Use POST method only for FOAF post request.")

            #Get the requester specified by request
            requester, _ = Author.objects.get_or_create(**data['author'])

            #Get intersection of post author's friends and requester's friends
            req_friends = data['friends']
            auth_friends = []
            for friend in getAllFriends(post.author.id):
                auth_friends.append(friend.friend_url)

            common_friends = list(set(req_friends) & set(auth_friends))

            #Case 1: User has visibility
            if common_friends or requester.url in auth_friends:
                serializer = PostSerializer(post)
                response = {}
                response['query'] = 'posts'
                response['post'] = serializer.data
                return Response(response)
            #Case 2: User does not have visibility
            else:
                return HttpResponseForbidden(b"You dont have visibility to this post.")
        except Exception as e:
            return HttpResponseServerError(e)
    #Method not allowed
    return HttpResponseNotAllowed()

#TODO: get_or_create
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedAndNode])
def handle_comments(request, post_id):
    '''
        GET: To get comments from visible posts
        POST: To add a comment to the visible post.
    '''
    #Handler GET requests
    if request.method == 'GET':
        try:
            #Get the post specified by request
            post = Post.objects.filter(id=post_id)
            if not post.exists():
                return HttpResponseNotFound("Post Not Found.")
            post = post[0]
            
            #Reject request if anonymous user or user does not have visibility
            if not checkVisibility(request.user, post):
                return HttpResponseForbidden(b"You dont have visibility.")
            
            #Valid request -> get comments data and return in response
            paginator = CustomPagination()
            comments = Comment.objects.filter(post=post).order_by('-published')
            try:
                comments = paginator.paginate_queryset(comments, request)
            except Exception as e:
                return HttpResponseNotFound(e)
            serializer = CommentSerializer(comments, many=True)
            response = paginator.get_paginated_response(query="comments", data_name='comments', data=serializer.data)
            return response
            
        #Server error when handling reqeust
        except Exception as e:
            return HttpResponseServerError(e)
        
    #Handler POST requests (add a comment to the post)
    elif request.method == 'POST':
        #Initialize response context
        context = {
                "query": "addComment",
                "success": False,
                "message": "Comment not Allowed",
            }
        try:
            #Parse comment form data from request
            data = json.loads(request.body)
            if not ('post' in data.keys() and 'comment' in  data.keys() and 'author' in data['comment'].keys()):
                return Response(context, status=403)
            post_info = data['post']
            comment_info = data['comment']
            author_info = comment_info['author']
            author_info['id'] = findAuthorIdFromUrl(author_info['id'])
            author_info['email'] = "{}@remote_user.com".format(author_info['id'])
            #Get target post object on local server
            post_id = findAuthorIdFromUrl(post_info)
            post = Post.objects.filter(id=post_id)
            if not post.exists():
                return Response(context, status=403)
            post = post[0]

            #Get comment author object on local server
            comment_author, _ = Author.objects.get_or_create(**author_info)

            #Check visibility
            if not checkVisibility(comment_author, post):
                return Response(context, status=403)
            
            comment_info['author'] = comment_author
            comment_info['post'] = post

            new_comment = Comment.objects.filter(**comment_info)
            if new_comment.exists():
                return Response(context, status=403)

            #Create a comment as required
            new_comment = Comment.objects.create(**comment_info)

            if new_comment:
                #return success response
                context['success'] = True
                context['message'] = "Comment Added"
                return Response(context, status=200)
            #comment create failed.
            else:
                return Response(context, status=403)

        #Server error when handling request       
        except Exception as e:
            return HttpResponseServerError(e)
    #Method not allowed
    else:
        return HttpResponseNotAllowed()


@api_view(['GET'])
@permission_classes([IsAuthenticatedAndNode])
def ViewProfile(request, author_id):
    '''
        GET: To get a author profile by given author id 
        POST: To update a author profile by given form.
        * Post method uses form instead of json format.
    '''
    if request.method == 'GET':
        try:
            #Get author whose profile to view
            author = Author.objects.filter(id=author_id)
            #Case 1: author's profile is found
            if author.exists():
                serializer = AuthorSerializer(author[0])
                return Response(serializer.data)
            #Case 2: author's profile is not found
            else:
                return HttpResponseNotFound(b"User Not found")
        #Server error when handling request
        except Exception as e:
             return HttpResponseServerError(e)
        #Method not allowed
    else:
        return HttpResponseNotAllowed()
    '''
    #Handling POST request (Updating a author's profile)
    elif request.method == 'POST':
        #check user authenticaiton first
        if request.user.is_anonymous or (author_id != request.user.id):
            return HttpResponseForbidden(b"Invalid user")
        try:
            #Get author whose profile to view
            author = Author.objects.filter(id=author_id)
            #Author's profile found
            if author.exists():
                serializer = AuthorSerializer(author[0], data=request.POST, partial=True)
                #Valid data -> update author's profile
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(serializer.data)
                #Invalid data -> return failure message
                else:
                    return HttpResponseForbidden(b"invalid author form data")
            #Author's profile not found
            else:
                return HttpResponseForbidden(b"Author not found")
        #Server error when handling request
        except Exception as e:
            return HttpResponseServerError(e)
    '''

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedAndNode])
def get_friendlist(request, author_id):
    '''
        GET: To get by friend list given author_id
        POST: method: post with  authors list and returns the friend of the given author
    '''
    #Handling GET requests
    if request.method == 'GET':
        try:
            #Get the friend instance of the specified author
            friend = Friend.objects.filter(friend_id=author_id)
            result = []

            #Append friend of specified author if any
            if friend.exists():
                friendships = Friendship.objects.filter(Q(author_a=friend[0]) | Q(author_b=friend[0]))
                #For each friendship, append the friend instance that is not the specified author
                for friendship in friendships:
                    if friendship.author_a.friend_id == author_id:
                        result.append(friendship.author_b.friend_url)
                    else:
                        result.append(friendship.author_a.friend_url)
                        
            #return result  
            serializer = FriendshipSerializer(result, exclude=['author'])
            return Response(serializer.data)

        #Server error when handling request
        except Exception as e:
            return HttpResponseServerError(e)
            
    #Handling POST request
    elif request.method == 'POST':
        try:
            #Parse author list from reqeust
            body = json.loads(request.body)
            authors = body['authors']
            friendIDList = []
            #Get the friend instance of the author
            author = Friend.objects.filter(friend_id=author_id)

            #No Friend object of author found, return an empty list of authors
            if not author.exists():
                serializer = FriendshipSerializer(
                    friendIDList, context={'author': author_id})
                return Response(serializer.data)

            author = Friend.objects.get(friend_id=author_id)
            #Add id of friends to result list if there is any
            for friend_id in authors:
                if checkFriendship(author.friend_id, friend_id):
                    friend = Friend.objects.get(friend_id=friend_id)
                    friendIDList.append(friend.friend_url)

            #return result
            serializer = FriendshipSerializer(
                friendIDList, context={'author': author.url})
            return Response(serializer.data)
        #Server error
        except Exception as e:
            return HttpResponseServerError(e)
    #Mehtod not allowed
    else:
        return HttpResponseNotAllowed()
        

@api_view(['GET'])
@permission_classes([IsAuthenticatedAndNode])
def check_friendship(request, author1_id, author2_id):
    '''
        GET: To check author 1 and author 2 are friend or not 
    '''
    #Handling GET request
    if request.method == 'GET':
        try:
            #Initialize response context
            context = {
                'query': 'friends',
                'friends': None,
                'authors': []
            }
            #TODO: return url instead and do parse id from url
            context['authors'].append(author1_id)
            context['authors'].append(author2_id)

            #Case 1: authors are in friendship
            if checkFriendship(author1_id, author2_id):
                context['friends'] = True
                return Response(context, status=200)
            #Case 2: authors are in friendship
            else:
                context['friends'] = False
                return Response(context, status=200)

        #Server Error
        except Exception as e:
            return HttpResponseServerError(e)
    #Method not allowed
    else:
        return HttpResponseNotAllowed


@api_view(['POST'])
@permission_classes([IsAuthenticatedAndNode])
def make_friendRequest(request):
    '''
        POST: To make a single frendrequest
    '''
    #Handling POST method
    if request.method == 'POST':
        try:
            #Initialize response context
            context = {
                'query': 'friends',
                'success': None,
                'authors': []
            }
            #TODO: use url field instead of id and parse id from url
            #Parser author info and friend info from request
            data = json.loads(request.body)
            author = data['author']
            friend = data['friend']

            author_from, _ = Friend.objects.get_or_create(**author)
            author_to, _ = Friend.objects.get_or_create(**friend)
            context['authors'].append(author_from.url)
            context['authors'].append(author_to.url)
    
            #Create a new friend request if authors are not friend and no such friend request exists
            friendship = checkFriendship(author_from.id, author_to.id)
            if not friendship:
                #mutual request means author A had requested author B as friend,
                #meanwhile author B sends a friendrequest to author A
                #Eventually, author A and author B become friends automatically.
                mutual_req = FriendRequest.objects.filter(
                    author_from=author_to, author_to=author_from)
                if mutual_req.exists():
                    mutual_req[0].delete()
                    if author_from.id < author_to.id:
                        Friendship.objects.create(
                            author_a=author_from, author_b=author_to)
                    else:
                        Friendship.objects.create(
                            author_a=author_to, author_b=author_from)

                    context['success'] = True
                    return Response(context, status=200)
                #mutual request does not exist
                else:
                    #Create a request as desired
                    request, created = FriendRequest.objects.get_or_create(
                        author_from=author_from, author_to=author_to)
                    if created:
                        context['success'] = True
                        return Response(context, status=200)
                    else:
                        context['success'] = False
                        return Response(context, status=200)

            #Friendship exists
            context['success'] = False
            return Response(context, status=200)
        #Server Error
        except Exception as e:
            print(e)
            return HttpResponseServerError(e)
    #Method not allowed
    else:
        return HttpResponseNotAllowed()

#helper funciton
def getVisiblePosts(requester, author=None):
    '''
        To a list of visible posts.
            parameter: 
                requster: a author requsts a list of posts.
                author: a author set posts unlisted or not
            return:
                result: a list of visble of posts.
    '''
    result = []
    #Anonymous user
    if requester.is_anonymous:
        if author:
            return Post.objects.filter(author=author, visibility='PUBLIC', unlisted=False).order_by('-published')
        else:
            return Post.objects.filter(visibility='PUBLIC', unlisted=False).order_by('-published')
    #Authenticated user
    if author:
        posts = Post.objects.filter(author=author, unlisted=False).order_by('-published')
    else:
        posts = Post.objects.filter(unlisted=False).order_by('-published')

    #Append post to result according to visibility and user's status
    for post in posts:
        #Self post or public post
        if post.visibility == 'PUBLIC' or post.author == requester:
            result.append(post)
        #Friends only post
        elif post.visibility == 'FRIENDS':
            if checkFriendship(post.author.id, requester.id):
                result.append(post)
        #Friend of a friend post
        elif post.visibility == 'FOAF':
            #user and author are in friendship
            if checkFriendship(post.author.id, requester.id):
                result.append(post)
            else:
                for friend in getAllFriends(post.author.id):
                    #user is in friendship with one of friends of the author
                    if checkFriendship(friend.id, requester.id):
                        result.append(post)
        #Server only post
        elif post.visibility == 'SERVERONLY':
            if post.author.host == requester.host:
                result.append(post)
        #TODO: Post is visible to user
        #if request.user.id in post.visibleTo and (not post in post_list / private post):
            #post_list.append(post)

    return result

def checkVisibility(requester, post):
    '''
        To check visibility of requester toward a post.
            parameter: 
                requester: a author want to see a post.
                post: a post which the requester wants to see.
            return:
                True: the requester is able to see the post
                False: the requester is not able to see the post
    '''
    #public post or self post
    if  post.visibility == 'PUBLIC' or post.author == requester:
        return True
    else:
        req_friendsList = getAllFriends(requester.id)
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
                    if checkFriendship(friend.id, post.id):
                        return True

        elif post.visibility == 'SERVERONLY':
            print("SERVERONLY unimplemented.But I give you visibility by this time.")
            if post.author.host == requester.host:
                return True
       #TODO: To check visibility within visibleTo
        #if request.user.id in post.visibleTo and (not post in post_list):
            #post_list.append(post)
    return False
