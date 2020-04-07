from .models import Friend, Friendship
from accounts.models import ServerNode
from django.db.models import Q
import urllib
import requests


def checkFriendship(friend1_id, friend2_id):
    '''
        given 2 authors check weather they're friends
    '''
    friend1_id = friend1_id.split('/')[-1]
    friend2_id = friend2_id.split('/')[-1]
    try:
        friend1 = Friend.objects.get(id=friend1_id)
        friend2 = Friend.objects.get(id=friend2_id)
    except Exception as e:
        return False

    if friend1.id < friend2.id:
        author_from, author_to = friend1, friend2
    else:
        author_from, author_to = friend2, friend1
    if Friendship.objects.filter(author_a=author_from, author_b=author_to).exists():
        return True
    else:
        return False

def checkFOAFship(friend, requester):
    has_visibility = False
    node = ServerNode.objects.filter(host_url__startswith=friend.host)
    #Check friendship if existing in friends of post author and requester.
    if node.exists():
        node = node[0]
        if checkRemoteFriendship(node, friend.url, requester.url):
            has_visibility = True
    return has_visibility

def getAllFriends(author_id):
    '''
        given an author id find all this user's friends
    '''
    friends = []
    try:
        author = Friend.objects.get(id=author_id)
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
    #PUBLIC post -> always true
    if post.visibility == 'PUBLIC':
        return True
    #invalid requster -> False expcept for public posts
    if not requester:
        return False
    else:
        if requester.id in post.visibleTo:
            return True
        #self post -> always true
        if post.author.id == requester.id:
            return True
        #friends related posts
        author = Friend.objects.filter(id=post.author.id)
        author = author[0] if author.exists() else None
        if author:
            req_friendsList = getAllFriends(requester.id)
            if post.visibility == 'FRIENDS':
                if author in req_friendsList:
                    return True
            elif post.visibility == 'FOAF':
                #Case1: author and requester are friends => return True
                if author in req_friendsList:
                    return True
                #Case2: author and a friend of requester are friends => return True
                else:
                    for friend in req_friendsList:
                        if checkFriendship(friend.id, author.id):
                            return True
        #server only post
        if post.visibility == 'SERVERONLY':
            if post.author.host == requester.host:
                return True
    return False

def SendFriendRequestRemote(author_form, friend_form):
    body = {
        'query': 'friendrequest',
        'author': author_form,
        'friend': friend_form,
    }
    node = ServerNode.objects.filter(
        host_url__startswith=body['friend']['host'])
    if not node.exists():
        return False
    node = node[0]
    url = "{}friendrequest".format(node.host_url)
    try:
        response = requests.post(url, json=body, auth=(
            node.server_username, node.server_password))
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        pass


def checkRemoteFriendslist(node, author_id, friends):
    body = {
        'query': 'friends',
        'author': author_id,
        'authors': friends
    }

    url = "{}author/{}/friends".format(node.host_url, author_id.split('/')[-1])
    try:
        response = requests.post(url, json=body, auth=(
            node.server_username, node.server_password))
        if response.status_code == 200:
            return response.json()['authors']
        else:
            return []
    except Exception as e:
        pass

def checkRemoteFriendship(node, url_node, url_req):
    author_id1 = url_node.split('/')[-1]
    author_id2 = urllib.parse.quote(url_req, safe='~()*!.\'')
    url = "{}author/{}/friends/{}".format(node.host_url, author_id1, author_id2)
    try:
        response = requests.get(url, auth=(node.server_username, node.server_password))
        if response.status_code == 200:
            return response.json()['friends']
        else:
            return False
    except Exception as e:
        print(e)
        return False



