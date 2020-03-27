from django.shortcuts import render, reverse, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
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
from .helper_functions import getVisiblePosts,getRemotePublicPosts,getNodePostComment,getNodePost,getNodeAuthorPosts,postNodePostComment
from friendship.helper_functions import checkVisibility
from .serializers import PostSerializer, CommentSerializer
from accounts.permissions import IsActivated, IsActivatedOrReadOnly, IsPostCommentOwner
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError, HttpResponseNotAllowed, HttpResponseForbidden
import base64
from rest_framework.renderers import JSONRenderer

Author = get_user_model()


class ViewPublicPosts(APIView):
    """
    View to  a list of public posts, checking visibility before display to user

    * Requires token authentication.
    * Only activated users are able to read-only this view.
    """
    #authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsActivatedOrReadOnly]

    def get(self, request, format=None):
        """
        Return a list of all public posts.
        """
        try:
            form = PostForm(request.POST or None)
            posts = getVisiblePosts(request.user)
            remote_posts = getRemotePublicPosts() 
            
            if len(remote_posts) > 0:
                posts = list(posts) + remote_posts
                posts.sort(key=lambda x: x.published, reverse=True)
            #Fixed: fix time order with remote posts
            context = {
                'post_list': posts[:20],
                'form': form,
            }
            return render(request, "posting/stream.html", context)
        except Exception as e:
            print(e)
            return HttpResponseServerError(e)
        #return a response instead

    def post(self, request, format=None):
        try:
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                form_data = form.cleaned_data
                contentType = form_data.get('contentType')
                if contentType in ['image/png;base64', 'image/jpeg;base64', 'application/base64']:
                    form_data['content'] = base64.b64encode(
                        request.FILES['image'].read()).decode("utf-8")
                form_data['author'] = request.user
                form_data.pop('image')
                newpost = Post.objects.create(**form_data)
                newpost.origin = "{}/posts/{}/".format(settings.HOSTNAME, str(newpost.id))
                print(newpost.origin)
                form = PostForm()
            else:
                return HttpResponseForbidden("invalid input")
        except Exception as e:
            print(e)
        return redirect('/posts/')
        #return a response instead


class ViewPostDetails(APIView):
    """
    View to a list a detail of post and its comments in the system.

    * Requires token authentication.
    * Only authenticated authors are able to access this view.
    """
    #authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id, format=None):
        """
        Return a detail of post by given Post Id.
        """
        post = Post.objects.filter(id=post_id)
        #Remote request
        if not post.exists():
            #TODO Find exactly one node instead of abusing all nodes. 
            nodes = ServerNode.objects.all()
            if nodes.exists():
                post = getNodePost(post_id, nodes)  # TODO USE GET_AUTH_POST!!!
            if post != None:
                comments = getNodePostComment(post)
            else:
                return HttpResponseNotFound("Post not found")
        #Local request
        else:
            post = Post.objects.get(id=post_id)
            if not checkVisibility(request.user, post):
                return HttpResponseForbidden("You don't have visibility.")
            comments = Comment.objects.filter(post=post)
        context = {
            'post': post,
            'comment_list': comments[:10],
        }
        return render(request, "posting/post-details.html", context)

#We are using POST method to delete.
#Need to use Delete Method to do this.
class DeletePost(APIView):
    """
    Delete to a post by given Post ID in the system.

    * Requires token authentication.
    * Only authenticated and its owner author is able to access this view.
    """

    #authentication_classes = [authentication.TokenAuthentication]
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
    #authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsActivated]

    def post(self, request, post_id, format=None):
        """
        Edit a post by given Post Id.
        """
        try:
            '''
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                form_data = form.cleaned_data
            contentType = form_data.get('contentType')
            if contentType in ['image/png;base64', 'image/jpeg;base64', 'application/base64']:
                form_data['content'] = base64.b64encode(request.FILES['image'].read()).decode("utf-8")
            '''
            form = request.POST
            post = Post.objects.filter(id=post_id)
            if post.exists():
                post = Post.objects.get(id=post_id)
                if request.user.has_perm('owner of post', post):
                    serializer = PostSerializer(post, data=form, context={
                                                'author': request.user}, partial=True)
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

    #authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsActivated]

    def post(self, request, post_id, comment_id=None, format=None):
        """
        Create a comment to a given Post Id.
        """
        try:
            #Target post on remote server
            post = Post.objects.filter(id=post_id)
            if not post.exists():
                node = ServerNode.objects.all()
                if node.exists():
                    #TODO: get autho post check visibility first 
                    post = getNodePost(post_id,node=node)
                    if post:
                        remote_comment = Comment(comment=request.POST['comment'],author=request.user,post=post)
                        postNodePostComment(remote_comment)
                        return HttpResponseRedirect(reverse('posting:view post details', args=(post_id,)), {})
                    else:
                        return HttpResponseNotFound("Post Not Found")
                    #TODO: POST A comment 
                    #postNodePostComment(post_id,comment_data=comment)
            #Target post on local server
            else:
                post = Post.objects.get(id=post_id)
            if not checkVisibility(request.user, post):
                return HttpResponseForbidden("You don't have visibility.")
            
            serializer = CommentSerializer(data=request.POST, context={'author': request.user, 'post': post})
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
            if not checkVisibility(request.user, post):
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
            if not checkVisibility(request.user, post):
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
    #authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, author_id, format=None):
        """
        Get a list of posts to a given Author Id.
        """
        try:
            author = Author.objects.filter(id=author_id)
            print(author)
            if not author.exists():
                return HttpResponseNotFound("Author Not Found")
            author = Author.objects.get(id=author_id)
            posts = getVisiblePosts(request.user, author)
            context = {
                "posts": posts,
                "allowEdit": True,
            }
            return render(request, "posting/user-post-list.html", context)
        except Exception as e:
            return HttpResponseServerError(e)
