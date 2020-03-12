from .models import Friendship, FriendRequest
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import get_user_model
Author = get_user_model()

#helper function
'''
    given 2 authors check weather they're friends
'''
def checkFriendship(author_a, author_b):
    if author_a < author_b:
        author_from, author_to = author_a, author_b
    else:
        author_from, author_to = author_b, author_a
    if Friendship.objects.filter(author_a=author_from, author_b=author_to).exists():
        return True
    else:
        return False

#helper funciton
'''
    given an author id find all this user's friends
'''
def getAllFriends(author_id):
    friends = []
    try:
        author = Author.objects.filter(id=author_id)[0]
        friendships = Friendship.objects.filter(
            Q(author_a=author) | Q(author_b=author))
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
    if request.method == 'POST':
        try:
            form = request.POST or None
            author_from = Author.objects.filter(id=form['author_from'])[0]
            author_to = Author.objects.filter(id=form['author_to'])[0]
            if author_from.id < author_to.id:
                a, b = author_from, author_to
            else:
                 a, b = author_to, author_from
            #check weather they're already friends
            friendship = Friendship.objects.filter(author_a=a, author_b=b)
            if not friendship.exists():
                friend_req = FriendRequest.objects.filter(author_from=author_from, author_to=author_to)
                #check weather friend request already sent
                if not friend_req.exists():
                    FriendRequest.objects.create(author_from=author_from, author_to=author_to)

        except Exception as e:
            print(e)

    return HttpResponseRedirect(reverse('accounts:view profile', args=(form['author_to'],)), {})

'''
    deal with friend request (either Accept or Decline)
'''
def handleRequest(request):
    form = request.POST or None
    if request.method == 'POST':
        try:
            fr = FriendRequest.objects.get(id=form['request_id'])
            author_from = Author.objects.filter(id=fr.author_from.id)[0]
            author_to = Author.objects.filter(id=fr.author_to.id)[0]
            fr2 = FriendRequest.objects.filter(author_from=author_to, author_to=author_from)
            fr.delete()
            if form['method'] == 'Accept':
                if fr2.exists:
                    fr2.delete()
                if author_from.id < author_to.id:
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
            friend_requests = FriendRequest.objects.filter(author_to=request.user)
            context['friend_requests'] = friend_requests
        except Exception as e:
                print(e)

    return render(request, 'friendship/friends_list.html', context)

'''
    delete a specified friend
'''
def deleteFriend(request):
    form = request.POST or None
    
    try:
        author = Author.objects.filter(id=request.user.id)[0]
        friend = Author.objects.filter(id=form['friend_id'])[0]
        if author.id < friend.id:
            a, b = author, friend
        else:
            a, b = friend, author
        friendship = Friendship.objects.get(author_a=a, author_b=b)
        friendship.delete()

    except Exception as e:
        print(e)
        
    return HttpResponseRedirect(reverse('friendship:get friends list', args=(request.user.id,)), {})
