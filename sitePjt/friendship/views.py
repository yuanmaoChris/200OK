from .models import Friendship, FriendRequest, Friend
from .helper_functions import getAllFriends, checkFriendship
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.permissions import IsActivated, IsActivatedOrReadOnly, IsPostCommentOwner
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed, HttpResponseForbidden
from rest_framework.views import APIView
Author = get_user_model()


class SendFriendRequestView(APIView):

    """
    View to  send a friend reqest, checking permission before sending to other authors.

    * Requires token authentication.
    * Only activated users are able to read-only this view.
    """
    #authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsActivated]

    def post(self, request, format=None):
        '''
        send friend request from one author to another
        '''
        try:
            form = request.POST
            form_from = {
                'friend_id': form.get('friend_from_friend_id'),
                'friend_displayName': form.get('friend_from_friend_displayName'),
                'friend_url': form.get('friend_from_friend_url'),
                'friend_host': form.get('friend_from_friend_host')
            }
            form_to = {
                'friend_id': form.get('friend_to_friend_id'),
                'friend_displayName': form.get('friend_to_friend_displayName'),
                'friend_url': form.get('friend_to_friend_url'),
                'friend_host': form.get('friend_to_friend_host')
            }
            friend_from, created_from = Friend.objects.get_or_create(**form_from)
            friend_to, created_to = Friend.objects.get_or_create(**form_to)
            if friend_from.friend_id < friend_to.friend_id:
                a, b = friend_from, friend_to
            else:
                a, b = friend_to, friend_from
            #check if there is an oppsite request
            fr = FriendRequest.objects.filter(author_from=friend_to, author_to=friend_from)
            if fr.exists():
                fr[0].delete()
                friendship = Friendship.objects.create(author_a=a, author_b=b)
            else:

                #check weather they're already friends
                friendship = Friendship.objects.filter(author_a=a, author_b=b)
                fr = FriendRequest.objects.filter(author_from=friend_from, author_to=friend_to)
                if not friendship.exists() and not fr.exists():
                    friend_req = FriendRequest.objects.create(author_from=friend_from, author_to=friend_to)

            return HttpResponseRedirect(reverse('accounts:view profile', args=(form_to['friend_id'],)), {})
        except Exception as e:
            return HttpResponseServerError(e)


class HandleRequestView(APIView):

    """
    View to handle of friendship requsts, checking permission before handling it.

    * Requires token authentication.
    * Only activated users are able to read-only this view.
    """
    #authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsActivated]

    def post(self, request, format=None):
        '''
            deal with friend request (either Accept or Decline)
        '''
        
        try:
            form = request.POST or None
            fr = FriendRequest.objects.filter(id=form['request_id'])
            if not fr.exists():
                return HttpResponseNotFound("Friend request does not exists")
            fr = FriendRequest.objects.get(id=form['request_id'])
            ##Update
            author_from = fr.author_from
            author_to = fr.author_to
            fr2 = FriendRequest.objects.filter(author_from=author_to, author_to=author_from)
            if fr2.exists:
                fr2.delete()
            fr.delete()

            if form['method'] == 'Accept':
                if author_from.friend_id < author_to.friend_id:
                    a, b = author_from, author_to
                else:
                    a, b = author_to, author_from
                friendship = Friendship.objects.filter(author_a=a, author_b=b)
                #build friendship if they were not friends
                if not friendship.exists():
                    friendship = Friendship(author_a=a, author_b=b)
                    friendship.save()
                return HttpResponseRedirect(reverse('friendship:get friends list', args=(request.user.id,)), {})
        except Exception as e:
            return HttpResponseServerError(e)


class FriendsRequestView(APIView):

    """
    View to handle of friendship requsts, checking permission before handling it.

    * Requires token authentication.
    * Only activated users are able to read-only this view.
    """
    '''
    list all friends requests 
    '''
    #authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsActivated]

    def get(self, request, format=None):
        try:
            context = {
                'friend_requests': None
            }
            friend_requests = FriendRequest.objects.filter(author_to=request.user)
            context['friend_requests'] = friend_requests
            return render(request, 'friendship/friend_request.html', context)
        except Exception as e:
                return HttpResponseServerError(e)


class GetFriendsListView(APIView):

    """
    View to get of friend list, checking permission before get it.

    * Requires token authentication.
    * Only activated users are able to read-only this view.
    """

    #authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsActivated]

    def get(self, request, author_id, format=None):
        '''
        list all friends
        '''
        try:
            context = {
                'author': request.user,
                'friends': [],
                'friend_requests': None

            }
            #get friend list
            context['friends'] = getAllFriends(author_id)
            #get friend requests
            friend = Friend.objects.filter(friend_id=request.user.id)
            if not friend.exists():
                friend = Friend(friend_id=request.user.id,
                                friend_displayName=request.user.displayName,
                                friend_host=request.user.host,
                                friend_url=request.user.url
                                )
                friend.save()
            friend = Friend.objects.get(friend_id=request.user.id)
            friend_requests = FriendRequest.objects.filter(author_to=friend)
            context['friend_requests'] = friend_requests
            return render(request, 'friendship/friends_list.html', context)
        except Exception as e:
            return HttpResponseServerError(e)


class DeleteFriendView(APIView):

    """
    View to delete of friendship requsts, checking permission before handling it.

    * Requires token authentication.
    * Only activated users are able to read-only this view.
    """

    #authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsActivated]

    def post(self, request, format=None):
        '''
        delete a specified friend
        '''
        try:
            form = request.POST or None
            author = Friend.objects.filter(friend_id=request.user.id)[0]
            friend = Friend.objects.filter(friend_id=form['friend_id'])[0]
            if author.friend_id < friend.friend_id:
                a, b = author, friend
            else:
                a, b = friend, author
            friendship = Friendship.objects.filter(author_a=a, author_b=b)
            if not friendship.exists():
                return HttpResponseNotFound("Delete failed. Friendship not found.")
            friendship = Friendship.objects.get(author_a=a, author_b=b)
            friendship.delete()
            return HttpResponseRedirect(reverse('friendship:get friends list', args=(request.user.id,)), {})
        except Exception as e:
            return HttpResponseServerError(e) 
