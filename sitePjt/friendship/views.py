from .models import Friendship, FriendRequest, Friend
from django.db.models import Q
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import get_user_model
Author = get_user_model()

#helper function

def checkFriendship(friend1_id, friend2_id):
    '''
        given 2 authors check weather they're friends
    '''
    try:
        friend1 = Friend.objects.get(friend_id=friend1_id)
        friend2 = Friend.objects.get(friend_id=friend2_id)
    except Exception as e:
        return False

    if friend1.friend_id < friend2.friend_id:
        author_from, author_to = friend1, friend2
    else:
        author_from, author_to = friend2, friend1
    if Friendship.objects.filter(author_a=author_from, author_b=author_to).exists():
        return True
    else:
        return False

#helper funciton

def getAllFriends(author_id):
    '''
        given an author id find all this user's friends
    '''
    friends = []
    try:
        author = Friend.objects.get(friend_id=author_id)
        friendships = Friendship.objects.filter(Q(author_a=author) | Q(author_b_id=author))
        for friendship in friendships:
            if friendship.author_a == author:
                friends.append(friendship.author_b)
            else:
                friends.append(friendship.author_a)
    except Exception as e:
            print(e)

    return friends

'''
    send friend request from one author to another
'''
def sendRequest(request):
    if request.user.activated:
        form = request.POST or None
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

        if request.method == 'POST':
            try:
                # form = request.POST or None
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
                    if not friendship:
                        friend_req = FriendRequest.objects.create(author_from=friend_from, author_to=friend_to)
                
            except Exception as e:
                print(e)

    return HttpResponseRedirect(reverse('accounts:view profile', args=(form_to['friend_id'],)), {})

'''
    deal with friend request (either Accept or Decline)
'''
def handleRequest(request):
    form = request.POST or None
    if request.method == 'POST' and request.user.activated:
        try:
            fr = FriendRequest.objects.get(id=form['request_id'])
            ##Update
            author_from= fr.author_from
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
                
        except Exception as e:
            print(e)
    return HttpResponseRedirect(reverse('friendship:get friends list', args=(request.user.id,)), {})

'''
    list all friends requests 
'''
def ViewFriendsRequest(request, author_id):
    context = {
        'friend_requests': None
    }
    if request.method == 'GET':
        try:
            #####################################################################
            friend_requests = FriendRequest.objects.filter(author_to=request.user)
            context['friend_requests'] = friend_requests
        except Exception as e:
                print(e)
    
    return render(request, 'friendship/friend_request.html', context)

'''
    list all friends
'''

def getFriendsList(request, author_id):
    context = {
        'author': request.user,
        'friends': [],
        'friend_requests': None
        
    }
    if request.method == 'GET':
        try:
            #get friend list
            context['friends'] = getAllFriends(author_id)
            #get friend requests
            friend = Friend.objects.get(friend_id=request.user.id)
            friend_requests = FriendRequest.objects.filter(author_to=friend)
            context['friend_requests'] = friend_requests
        except Exception as e:
                print(e)

    return render(request, 'friendship/friends_list.html', context)

'''
    delete a specified friend
'''
def deleteFriend(request):
    if request.user.activated:
        form = request.POST or None
        
        try:
            author = Friend.objects.filter(friend_id=request.user.id)[0]
            friend = Friend.objects.filter(friend_id=form['friend_id'])[0]
            if author.friend_id < friend.friend_id:
                a, b = author, friend
            else:
                a, b = friend, author
            friendship = Friendship.objects.get(author_a=a, author_b=b)
            friendship.delete()

        except Exception as e:
            print(e)
        
    return HttpResponseRedirect(reverse('friendship:get friends list', args=(request.user.id,)), {})
