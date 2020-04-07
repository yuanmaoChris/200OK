from django.shortcuts import render, reverse, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)
from django.contrib.auth import get_user_model
from django.conf import settings
from .forms import PostForm
from .models import Post, Comment
from accounts.models import ServerNode
from .helper_functions import getVisiblePosts, getRemotePublicPosts, getRemotePostComment, getRemotePost, getRemoteAuthorPosts, postRemotePostComment, getRemoteFOAFPost
from friendship.helper_functions import checkVisibility, getAllFriends
from .serializers import PostSerializer, CommentSerializer
from accounts.permissions import IsActivated, IsActivatedOrReadOnly, IsPostCommentOwner
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError, HttpResponseNotAllowed, HttpResponseForbidden
import base64
from rest_framework.renderers import JSONRenderer

Author = get_user_model()


class ViewPublicPosts(APIView):
    """
    View to  a list of public posts, checking visibility before display to user

    * Requires token authentication.
    * Only activated users are able to read-only this view.
    """
    permission_classes = [IsActivatedOrReadOnly]
    def get(self, request, format=None):
        """
        Return a list of all public posts.
        """
        try:
            posts = getVisiblePosts(request.user)
            posts.sort(key=lambda x: x.published, reverse=True)
            context = {
                'post_list': posts[:20],
            }
            return render(request, "posting/stream.html", context)
        except Exception as e:
            print(e)
            return HttpResponseServerError(e)

    def post(self, request, format=None):
        try:
            form = PostForm(request.POST, request.FILES)
            print(request.POST)
            if form.is_valid():
                form_data = form.cleaned_data
                contentType = form_data.get('contentType')
                if contentType in ['image/png;base64', 'image/jpeg;base64', 'application/base64']:
                    form_data['content'] = base64.b64encode(
                        request.FILES['image'].read()).decode("utf-8")
                form_data['author'] = request.user
                form_data.pop('image')
                newpost = Post.objects.create(**form_data)
                newpost.origin = "{}posts/{}".format(
                    settings.HOSTNAME, str(newpost.id))
                #TODO
                #uncomment this, change origin editable to true
                #newpost.save()
                response = PostSerializer(newpost).data
                return JsonResponse(response, status=200)
            else:
                return HttpResponseForbidden("Invalid Input")
        except Exception as e:
            print(e)
            return HttpResponseServerError(e)


class ViewPostDetails(APIView):
    """
    View to a list a detail of post and its comments in the system.

    * Requires token authentication.
    * Only authenticated authors are able to access this view.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, post_id, format=None):
        """
        Return a detail of post by given Post Id.
        """
        post = Post.objects.filter(id=post_id)
        #Remote request
        if not post.exists():
            nodes = ServerNode.objects.all()
            if nodes.exists():
                post, comments = getRemotePost(post_id, nodes, request.user.url)
            # if post != None:
            #     comments = getRemotePostComment(post, request.user.url)
            if not post:
                #TODO handle try three server foaf
                friends_obj = getAllFriends(request.user.id)
                friends = []
                for obj in friends_obj:
                    friends.append(obj.url)
                nodes = ServerNode.objects.all()
                if nodes.exists():
                    for node in nodes:
                        post, comments = getRemoteFOAFPost(
                            node, post_id, request.user, friends)
                        if post:
                            print(post.author)
                            break
            if not post:
                return HttpResponseNotFound("Post not found")
        #Local request
        else:
            post = post[0]
            if not checkVisibility(request.user.url, post):

                return HttpResponseForbidden("You don't have visibility.")
            comments = Comment.objects.filter(post=post)
        context = {
            'post': post,
            'comment_list': comments[:10],
        }
        return render(request, "posting/post-details.html", context)


class DeletePost(APIView):
    """
    Delete to a post by given Post ID in the system.

    * Requires token authentication.
    * Only authenticated and its owner author is able to access this view.
    """

    permission_classes = [IsActivated]

    def post(self, request, post_id, format=None):
        """
        Deleting to a post by given Post Id.
        """
        try:
            post = Post.objects.filter(id=post_id)
            if not post.exists():
                return HttpResponseNotFound("Post not found.")
            post = Post.objects.get(id=post_id)
            if request.user.has_perm('owner of post', post):
                post.delete()
            else:
                return HttpResponseForbidden("You must be the owner of this post.")
            return HttpResponseRedirect(reverse('posting:view user posts', args=(request.user.id,)), {})

        except Exception as e:
            return HttpResponseServerError(e)


class EditPost(APIView):
    """
    Edit to a post by given Post ID in the system.

    * Requires token authentication.
    * Only authenticated and its owner author is able to access this view.
    """
    '''
    use POST to resend a form to update an existing post
    '''
    permission_classes = [IsActivated]
    def post(self, request, post_id, format=None):
        """
        Edit a post by given Post Id.
        """
        try:
            form = request.POST.copy()
            try:
                if request.FILES['image']:
                    form['content'] = base64.b64encode(request.FILES['image'].read()).decode("utf-8")
            except Exception as e:
                print("Error when checking if an image is uploaded")
                print(e)

            post = Post.objects.filter(id=post_id)
            if post.exists():
                post = Post.objects.get(id=post_id)
                if request.user.has_perm('owner of post', post):
                    serializer = PostSerializer(post, data=form, context={'author': request.user}, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return HttpResponseRedirect(reverse('posting:view user posts', args=(request.user.id,)), {})
                    else:
                        print(serializer.errors)
                        return Response("Save failed. Invalid data",)
                else:
                    return HttpResponseForbidden("You must be the owner of this post.")
            else:
                return HttpResponseNotFound()
        except Exception as e:
            return HttpResponseServerError(e)


class CommentHandler(APIView):
    """
    Create or Delete a comment to a Post to a given Post ID in the system.

    * Requires token authentication.
    * Only authenticated author is able to access this view.
    """


    permission_classes = [IsActivated]
    def post(self, request, post_id, comment_id=None, format=None):
        """
        Create a comment to a given Post Id.
        """
        try:
            post_host = request.POST.get('post_origin', None)
            if post_host:
                post_host = post_host.split('posts/')[0]
            #Target post on remote server
            if post_host and not post_host == settings.HOSTNAME:
                nodes = ServerNode.objects.filter(host_url__startswith=post_host)
                if nodes.exists():
                    post, _ = getRemotePost(post_id, nodes, request.user.url)
                    if not post:
                        friends = []
                        friend_objs = getAllFriends(request.user.id)
                        for obj in friend_objs:
                            friends.append(obj.url)
                        node = nodes[0]
                        post, _ = getRemoteFOAFPost(node, post_id, request.user, friends)
                    if post:
                        remote_comment = Comment(
                            comment=request.POST['comment'], author=request.user, post=post,contentType=request.POST['contentType'])
                        if postRemotePostComment(remote_comment, request.user.url):
                            return HttpResponseRedirect(reverse('posting:view post details', args=(post_id,)), {})
                        else:
                            return HttpResponseForbidden("Remote comment failed.")
                return HttpResponseNotFound("Post Not Found")
            #Target post on local server
            else:
                post = Post.objects.filter(id=post_id)
                if not post.exists():
                    return HttpResponseNotFound("Post not found.")
            post = post[0]
            if not checkVisibility(request.user.url, post):
                return HttpResponseForbidden("You don't have visibility.")

            serializer = CommentSerializer(data=request.POST, context={
                                           'author': request.user, 'post': post})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return HttpResponseRedirect(reverse('posting:view post details', args=(post_id,)), {})
            else:
                return Response("Comment save failed. Invalid data")
        except Exception as e:
            return HttpResponseServerError(e)

    def delete(self, request, post_id, comment_id=None, format=None):
        '''
        delete a specified comment by its comment_id
        '''
        try:
            post = Post.objects.filter(id=post_id)
            if not post.exists():
                return HttpResponseNotFound("Post Not Found")
            post = Post.objects.get(id=post_id)
            if not checkVisibility(request.user.url, post):
                return HttpResponseForbidden("You don't have visibility.")

            comment = Comment.objects.filter(id=comment_id)
            if not comment.exists():
                return HttpResponseNotFound("Comment Not Found")
            comment = Comment.objects.get(id=comment_id)

            if request.user.has_perm('owner of comment', comment):
                comment.delete()
                return HttpResponseRedirect(reverse('posting:view post details', args=(post_id,)), {})
            else:
                return HttpResponseForbidden("You must be the owner of this comment.")

        except Exception as e:
            return HttpResponseServerError(e)

    #To be removed
    def get(self, request, post_id, comment_id=None, format=None):
        '''
        delete a specified comment by its comment_id
        '''
        try:
            post = Post.objects.filter(id=post_id)
            if not post.exists():
                return HttpResponseNotFound("Post Not Found")
            post = Post.objects.get(id=post_id)
            if not checkVisibility(request.user.url, post):
                return HttpResponseForbidden("You don't have visibility.")

            comment = Comment.objects.filter(id=comment_id)
            if not comment.exists():
                return HttpResponseNotFound("Comment Not Found")
            comment = Comment.objects.get(id=comment_id)

            if request.user.has_perm('owner of comment', comment):
                comment.delete()
                return HttpResponseRedirect(reverse('posting:view post details', args=(post_id,)), {})
            else:
                return HttpResponseForbidden("You must be the owner of this comment.")

        except Exception as e:
            return HttpResponseServerError(e)


class ViewUserPosts(APIView):
    """
    View to a list of Posts to a given Author ID in the system.

    * Requires token authentication.
    * Only authenticated and own author is able to access this view.
    """
    '''
    show a specified author's posts.
    '''

    permission_classes = [IsAuthenticated]
    def get(self, request, author_id, format=None):
        """
        Get a list of posts to a given Author Id.
        """
        try:
            author = Author.objects.filter(id=author_id)
            if not author.exists():
                return HttpResponseNotFound("Author Not Found")
            author = Author.objects.get(id=author_id)
            posts = getVisiblePosts(request.user, author)
            posts.sort(key=lambda x: x.published, reverse=True)
            context = {
                "posts": posts,
                "allowEdit": True,
            }
            return render(request, "posting/user-post-list.html", context)
        except Exception as e:
            return HttpResponseServerError(e)
