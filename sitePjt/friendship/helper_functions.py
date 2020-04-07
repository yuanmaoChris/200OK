from .models import Friend, Friendship
from accounts.models import ServerNode
from django.db.models import Q
import urllib
import requests
from django.conf import settings


def checkFriendship(friend1_url, friend2_url):
    '''
        given two authors' url check weather they're friends
        Note: This funciton asserts the first author is from local
    '''
    friend1_id = friend1_url.split('/')[-1]
    friend2_id = friend2_url.split('/')[-1]
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

def getAllFriends(author_id):
    '''
        given an author id find all this user's friends
    '''
    friends = []
    try:
        print("Here")
        author = Friend.objects.get(id=author_id)
        friendships = Friendship.objects.filter(
            Q(author_a=author) | Q(author_b=author))
        print("here2")
        for friendship in friendships:
            if friendship.author_a == author:
                friends.append(friendship.author_b)
            else:
                friends.append(friendship.author_a)
    except Exception as e:
            print(e)
    print(friends)
    return friends

def checkFOAFriendship(friend1_url, friend2_url):
    '''
        given two authors' url check weather they're friends
        Note: This funciton asserts the first author is from local
    '''
    isFOAF = False
    friend1_id = friend1_url.split('/')[-1]
    friend2_id = friend2_url.split('/')[-1]

    friend1 = Friend.objects.filter(id=friend1_id)
    #friend1 is not in friendship with anyone
    if not friend1.exists():
        return False
    friend1 = friend1[0]
    #Friend2 is a friend with any local author
    if checkFriendship(friend1.id, friend2_id):
        return True
    
    #Friend2 is a friend with a friend B whom is a friend of friend1
    friendsList_local = getAllFriends(friend1.id)
    for friendObj in friendsList_local:
        #B is a local author
        if settings.HOSTNAME in friendObj.host:
            if checkFriendship(friendObj.id, friend2_id):
                return True
            else:
                continue
        #B is a remote author
        else:
            node = ServerNode.objects.filter(host_url__startswith=friendObj.host)
            if node.exists():
                node = node[0]
                if checkRemoteFriendship(node, friendObj.url, friend2_url):
                    return True
    return False

def checkVisibility(requester_url, post):
    '''
        To check visibility of requester toward a post.
            parameter: 
                requester: a author want to see a post. (Friend Object on local server)
                post: a post which the requester wants to see. (Local Post)

                True: the requester is able to see the post

                False: the requester is not able to see the post
    '''
    #PUBLIC post -> always true
    if post.visibility == 'PUBLIC':
        return True
    #invalid requster -> False expcept for public posts
    if not requester_url:
        return False

    if requester_url in post.visibleTo:
        return True

    if post.author.url == requester_url:
        return True


    #Server only post
    if post.visibility == 'SERVERONLY':
        return post.author.host in requester_url

    author = Friend.objects.filter(id=post.author.id)
    author = author[0] if author.exists() else None
    
    if author:  # friend object
        friendObjList = getAllFriends(author.id)
        friendsUrlList = []
        for friendObj in friendObjList:
            friendsUrlList.append(friendObj.url)
        if post.visibility == 'FRIENDS':
            if requester_url in friendsUrlList:
                return True
        elif post.visibility == 'FOAF':
            return checkFOAFriendship(post.author.url, requester_url)
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



