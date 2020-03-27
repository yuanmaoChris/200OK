from .models import Friend, Friendship
from accounts.models import ServerNode
from django.db.models import Q
import requests

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

def getAllFriends(author_id):
    '''
        given an author id find all this user's friends
    '''
    friends = []
    try:
        author = Friend.objects.get(id=author_id)
        friendships = Friendship.objects.filter(Q(author_a=author) | Q(author_b=author))
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
    #public post or self post
    if post.visibility == 'PUBLIC' or post.author == requester:
        return True
    else:
        req_friendsList = getAllFriends(requester.id)
        author = Friend.objects.get(friend_id=post.author.id)
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
                    if checkFriendship(friend.id, post.author.id):
                        return True

        elif post.visibility == 'SERVERONLY':
            print("SERVERONLY unimplemented.But I give you visibility by this time.")
            return True
            if post.author.host == requester.host:
                return True
       #TODO: To check visibility within visibleTo
        #if request.user.id in post.visibleTo and (not post in post_list):
            #post_list.append(post)
    return False


def SendFriendRequestRemote(author_form, friend_form):
    body = {
        'query': 'friendrequest',
        'author': author_form,
        'friend': friend_form,
    }
    node = ServerNode.objects.filter(host_url=body['friend']['host']+'service/')
    if not node.exists():
        return False
    node = node[0]
    url = "{}friendrequest".format(node.host_url)
    print(url)
    response = requests.post(url, json=body,auth=(node.server_username, node.server_password))
    print(body)
    # node = ServerNode.objects.all()
    # url = node[0].host_url
    # post_id = body['post'].split('/')[-2]
    # url = url + 'posts/{}/comments/'.format(str(post_id))
    # response = requests.post(url, json=body, auth=(
    #     node[0].server_username, node[0].server_password))
    if response.status_code == 200:
        return True
    else:
        return False
