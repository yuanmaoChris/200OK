from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings
import urllib
import json
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed, HttpResponseForbidden
from accounts.models import ServerNode
from posting.models import Post, Comment
from friendship.models import Friendship, FriendRequest,Friend
from posting.forms import CommentForm
from friendship.helper_functions import checkFriendship, getAllFriends, checkRemoteFriendslist, checkRemoteFriendship,checkFOAFship
from .serializers import PostSerializer, AuthorSerializer, CommentSerializer, FriendshipSerializer
from .permissions import IsAuthenticatedAndNode, IsShare
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
@permission_classes([IsAuthenticatedAndNode, IsShare])
def view_public_post(request):
    '''
        GET: To get all public posts 
    '''
    if request.method == 'GET':
        try:
            paginator = CustomPagination()
            requester = None
            if 'HTTP_X_USER_ID' in request.META.keys():
                requester_id = request.META.get('HTTP_X_USER_ID')
                requester = Friend.objects.filter(id=requester_id)
                requester = requester[0] if requester.exists() else None
            posts = getVisiblePosts(requester, author=None, IsShareImg=request.user.has_perm('share_image'))
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

@api_view(['GET'])
@permission_classes([IsAuthenticatedAndNode, IsShare])
def handle_auth_posts(request):
    '''
        GET:To get posts with authenticated requester
        POST: To add a post with authenticated requester
    '''
    #Handle GET requests
    if request.method == 'GET':
        try:
            #Parse requester information from node request
            if not 'HTTP_X_USER_ID' in request.META.keys():
                return HttpResponseForbidden("Who's requesting posts? Put author info in request headers under 'x-user-id'")
            requester_id = request.META.get('HTTP_X_USER_ID')
            requester = Friend.objects.filter(id=requester_id)
            requester = requester[0] if requester.exists() else None
            #Get all posts that requester has visitbility of
            posts = getVisiblePosts(requester, IsShareImg=request.user.has_perm("share_image"))
            paginator = CustomPagination()
            try:
                posts = paginator.paginate_queryset(posts, request)
            except Exception as e:
                return HttpResponseNotFound(e)
            serializer = PostSerializer(posts, many=True)
            #Add on pagination
            response = paginator.get_paginated_response('posts', 'posts', serializer.data)
            return response
            return Response(serializer.data)
        except Exception as e:
            return HttpResponseServerError(e)

    #Method not allowed
    else:
        return HttpResponseNotAllowed()

@api_view(['GET'])
@permission_classes([IsAuthenticatedAndNode, IsShare])
def view_author_posts(request, author_id):
    '''
       G To get all visiable posts by given author
    '''    
    #Handle GET request
    if request.method == 'GET':
        try:

            if not 'HTTP_X_USER_ID' in request.META.keys():
                return HttpResponseForbidden("Who's requesting posts? Put author info in request headers under 'x-user-id'")
            requester_id = request.META.get('HTTP_X_USER_ID')
            requester = Friend.objects.filter(id=requester_id)
            requester = requester[0] if requester.exists() else None
            #Get author instance whose posts to view
            author = Author.objects.filter(id=author_id)
            if not author.exists():
                return HttpResponseNotFound("Author Profile Not Found.")
            author = author[0]
            #filter out all posts that requester does not have visibility of
            posts = getVisiblePosts(requester, author, request.user.has_perm("share_image"))
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


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedAndNode, IsShare])
def view_single_post(request, post_id):
    '''
        GET: To get a single visiable post by given post id 
    '''
    if request.method == 'GET':
        try:
            if not 'HTTP_X_USER_ID' in request.META.keys():
                return HttpResponseForbidden("Who's requesting posts? Put author info in request headers under 'x-user-id'")
            requester_id = request.META.get('HTTP_X_USER_ID')
            requester = Friend.objects.filter(id=requester_id)
            requester = requester[0] if requester.exists() else None
            #Get the post specified by request
            post = Post.objects.filter(id=post_id)
            if not post.exists():
                return HttpResponseNotFound("Post Not Found.")
            post = post[0]
            #Case 1: User has visibility
            if checkVisibility(requester, post):
                serializer = PostSerializer(post)
                response = {}
                response['query'] = 'posts'
                #response['count'] = 1
                response['post'] = serializer.data
                return Response(response)
                
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
            #Validate request body
            if not ('postid' in data.keys() and 'url' in data.keys() and 'author' in data.keys() and 'friends' in data.keys()):
                return Response("Invalid request data", status=403)
            
            #Get the post specified by request
            post = Post.objects.filter(id=data['postid'])
            if not post.exists():
                return HttpResponseNotFound("Post Not Found.")
            post = post[0]

            if not post.visibility == "FOAF":
                return HttpResponseForbidden("Please POST to this API view only for FOAF post request.")
            
            #Frist Check -> get friends of requestor A from A's server
            friends = data['friends']
            node = ServerNode.objects.filter(host_url__startswith = data['author']['host'])
            if not node.exists():
                return HttpResponseForbidden("Requestor does not have visiblity of post.")
            node = node[0]
            friendsRequestor = checkRemoteFriendslist(node, data['author']['url'], friends)
            # friendsRequestor = friends
            #Second check -> get friends of post author B from B's server
            friendsAuthor = []
            friends = getAllFriends(post.author.id)
            for friend in friends:
                friendsAuthor.append(friend.url)
            #Third check -> get friendslist A intersects friendslist B as common friends
            #check until one of these common friends' servers confirm that A is a friend.
            friendsInCommom = list(set(friendsAuthor) & set(friendsRequestor))
            hasVisibility = False
            for friend_url in friendsInCommom:
                host = friend_url.split('author')[0]
                node = ServerNode.objects.filter(host_url__startswith = host)
                if node.exists():
                    node = node[0]
                    #once it is verified via the 3 hosts -> approve request.
                    if checkRemoteFriendship(node, friend_url, data['author']['url']):
                        hasVisibility = True
                        break

            #Case 1: User has visibility
            if hasVisibility:
                serializer = PostSerializer(post)
                response = {}
                response['query'] = 'posts'
                response['post'] = serializer.data
                return Response(response)
            #Case 2: User does not have visibility
            else:
                return HttpResponseForbidden("You dont have visibility to this post.")
        except Exception as e:
            print(e)
            return HttpResponseServerError(e)
    #Method not allowed
    return HttpResponseNotAllowed()


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedAndNode, IsShare])
def handle_comments(request, post_id):
    '''
        GET: To get comments from visible posts
        POST: To add a comment to the visible post.
    '''
    #Handler GET requests
    if request.method == 'GET':
        try:
            if not 'HTTP_X_USER_ID' in request.META.keys():
                return HttpResponseForbidden("Who's requesting posts? Put author info in request headers under 'x-user-id'")
            requester_id = request.META.get('HTTP_X_USER_ID')
            requester = Friend.objects.filter(id=requester_id)
            requester = requester[0] if requester.exists() else None
            #Get the post specified by request
            post = Post.objects.filter(id=post_id)
            if not post.exists():
                return HttpResponseNotFound("Post Not Found.")
            post = post[0]
            
            #Reject request if anonymous user or user does not have visibility
            if not checkVisibility(requester, post):
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

            #Check if comment author has visibility of post
            requester_id = author_info['id']
            requester = Friend.objects.filter(id=requester_id)
            requester = requester[0] if requester.exists() else None
            #Check visibility
            if not checkVisibility(requester, post):
                has_visibility = False
                #check visibility of case involving three servers
                if post.visibility == "FOAF": 
                    #Get all friends of post author
                    friends = getAllFriends(post.author.id)
                    for friend in friends:
                        node = ServerNode.objects.filter(host_url__startswith=friend.host)
                        #Check friendship if existing in friends of post author and requester.
                        if node.exists():
                            node = node[0]
                            if checkRemoteFriendship(node, friend.url, author_info['url']):
                                has_visibility = True
                                break
                if not has_visibility:
                    return Response(context, status=403)


            #Get comment author object on local server
            comment_author, _ = Author.objects.get_or_create(**author_info)
            
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
@permission_classes([IsAuthenticatedAndNode, IsShare])
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
            friend = Friend.objects.filter(id=author_id)
            result = []

            #Append friend of specified author if any
            if friend.exists():
                friendships = Friendship.objects.filter(Q(author_a=friend[0]) | Q(author_b=friend[0]))
                #For each friendship, append the friend instance that is not the specified author
                for friendship in friendships:
                    if friendship.author_a.id == author_id:
                        result.append(friendship.author_b.url)
                    else:
                        result.append(friendship.author_a.url)
                        
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
            author = body['author']
            response = {'query': 'friends', 'author': author}
            friendIDList = []
            #Get the friend instance of the author
            friend_author = Friend.objects.filter(url=author)

            #No Friend object of author found, return an empty list of authors
            if not friend_author.exists():
                response['authors'] = friendIDList
                return Response(response)

            friend_author = friend_author[0]
            #Add id of friends to result list if there is any
            for friend_id in authors:
                if checkFriendship(friend_author.id, friend_id):
                    friendIDList.append(friend_id)
            #return result
            response['authors'] = friendIDList
            return Response(response)
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
            author1_url = "{}author/{}".format(settings.HOSTNAME, author1_id)
            author2_id = "http://" + author2_id
            context['authors'].append(author1_url)
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
            return HttpResponseServerError(e)
    #Method not allowed
    else:
        return HttpResponseNotAllowed()

#helper funciton
def getVisiblePosts(requester, author=None, IsShareImg=False):
    '''
        To a list of visible posts.
            parameter: 
                requster: a author requsts a list of posts.
                author: a author set posts unlisted or not
            return:
                result: a list of visble of posts.
    '''
    bannedType = "_" if IsShareImg else "image"
    result = set()
    #Anonymous user
    if not requester:
        if author:
            return Post.objects.filter(Q(author=author, visibility='PUBLIC', unlisted=False) & ~Q(contentType__contains=bannedType)).order_by('-published')
        else:
            return Post.objects.filter(Q(visibility='PUBLIC', unlisted=False) & ~Q(contentType__contains=bannedType)).order_by('-published')
    #Authenticated user
    if author:
        posts = Post.objects.filter(Q(author=author, unlisted=False) & ~Q(contentType__contains=bannedType)).order_by('-published')
    else:
        posts = Post.objects.filter(Q(unlisted=False) & ~Q(contentType__contains=bannedType)).order_by('-published')

    #Append post to result according to visibility and user's status
    for post in posts:
        #Self post or public post
        if post.visibility == 'PUBLIC' or post.author.id == requester.id:
            result.add(post)
        #Friends only post
        elif post.visibility == 'FRIENDS':
            if checkFriendship(post.author.id, requester.id):
                result.add(post)
        #Friend of a friend post
        elif post.visibility == 'FOAF':
            #user and author are in friendship
            if checkFriendship(post.author.id, requester.id):
                result.add(post)
            else:
                for friend in getAllFriends(post.author.id):
                    #user is in friendship with one of friends of the author
                    if checkFriendship(friend.id, requester.id):
                        result.add(post)
                   #Adding:
                    if checkFOAFship(post.author, requester):
                        result.add(post)
        #Server only post
        elif post.visibility == 'SERVERONLY':
            if post.author.host == requester.host:
                result.add(post)
        else:
            print(requester.id, post.visibleTo)
            if requester.id in post.visibleTo:
                result.add(post)

    return list(result)

def checkVisibility(requester, post):
    '''
        To check visibility of requester toward a post.
            parameter: 
                requester: a author want to see a post. (Friend Object on local server)
                post: a post which the requester wants to see. (Local Post)
            return:
                True: the requester is able to see the post
                False: the requester is not able to see the post
    '''
    #PUBLIC post -> always true
    if  post.visibility == 'PUBLIC':
        return True
    #invalid requster -> False expcept for public posts
    if not requester:
        return False
    if requester.id in post.visibleTo:
        return True

    if post.author.id == requester.id:
        return True

    #Server only post
    if post.visibility == 'SERVERONLY':
        return post.author.host == requester.host 

    #From here...... add remote case
    #post author must have at least one friendship
    #friends related posts
    author = Friend.objects.filter(id=post.author.id)
    author = author[0] if author.exists() else None
    if author: #friend object
        #this line limits three server case, get post author's friends list and starts from there
        req_friendsList = getAllFriends(requester.id)
        if post.visibility == 'FRIENDS':
            if author in req_friendsList:
                return True
        elif post.visibility == 'FOAF':
            #Case1: author and requester are friends => return True
            if author in req_friendsList:
                return True
            #Case2: author and a friend of requester are friends => return True
            #must send a request(to 1.local server, 2.reqeust server, 3.other server)
            else:
                for friend in req_friendsList:
                    if checkFriendship(friend.id, author.id):
                        return True
    return False
