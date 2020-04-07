from django.db.models import Q
from accounts.models import Author
from posting.models import Post
from friendship.helper_functions import getAllFriends, checkFriendship, checkRemoteFriendship, checkVisibility, checkFOAFriendship


def getVisiblePosts(requester_url, author_url=None, IsShareImg=False):
    '''
        To a list of visible posts.
            parameter: 
                requster: an author url of whom the requst on behalf.
                author: an local author url 
            return:
                result: a list of visble of posts.
    '''
    bannedType = "_" if IsShareImg else "image"
    result = []
    if author_url:
        author = Author.objects.get(url=author_url)
        posts = Post.objects.filter(Q(author=author, unlisted=False) & ~Q(
            contentType__contains=bannedType)).order_by('-published')
    else:
        posts = Post.objects.filter(Q(unlisted=False) & ~Q(
            contentType__contains=bannedType)).order_by('-published')

    #Append post to result according to visibility and user's status
    for post in posts:
        if checkVisibility(requester_url, post):
            result.append(post)
    return result


