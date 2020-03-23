from friendship.helper_functions import checkFriendship, getAllFriends
from .models import Post, Comment

#helper funciton
'''
    get all visible posts, depends on the state of current user

    POST_VISIBILITY = (
    ('PUBLIC', 'Public'),
    ('PRIVATE', 'Prviate to self'),
    ('FRIENDS', 'Private to friends'),
    ('FOAF', 'Private to friends of friends'),
    ('SERVERONLY', 'Private to local friends'),
    )

'''

def getVisiblePosts(requester, author=None):
    result = []
    #the current user hasn't login yet, show some random public posts
    if requester.is_anonymous:
        if author:
            return Post.objects.filter(author=author, visibility='PUBLIC', unlisted=False).order_by('-published')
        else:
            return Post.objects.filter(visibility='PUBLIC', unlisted=False).order_by('-published')

    #only check one author's posts or all posts
    if author:
        posts = Post.objects.filter(author=author, unlisted=False).order_by('-published')
    else:
        posts = Post.objects.filter(unlisted=False).order_by('-published')

    for post in posts:
        if post.author == requester:  # my post
            result.append(post)
        elif post.visibility == 'PUBLIC':  # everyone can see's post
            result.append(post)
        elif post.visibility == 'FRIENDS':  # if friends then append this post
            if checkFriendship(post.author.id, requester.id):
                result.append(post)
        elif post.visibility == 'FOAF':  # friends of friends also can see
            if checkFriendship(post.author.id, requester.id):
                result.append(post)
            else:
                for friend in getAllFriends(post.author.id):
                    if checkFriendship(friend.friend_id, requester.id):
                        result.append(post)
        elif post.visibility == 'SERVERONLY':  # requires to be local friends
            if post.author.host == requester.host:
                result.append(post)
            print("SERVERONLY unimplemented.")
    if author == requester:
        unlisted_posts = Post.objects.filter(author=author, unlisted=True)
        for post in unlisted_posts:
            result.append(post)

    return result
