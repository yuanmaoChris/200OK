from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from datetime import datetime
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly
    )

from .models import Post, Comment


from .forms import PostNewForm, CommentForm
from .serializers import *
from .models import Post###, VisibleTo
from friendship import views as FriendshipViews

User = get_user_model()

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
            return Post.objects.filter(author=author, visibility='PUBLIC',unlisted=False).order_by('-published')
        else:
            return Post.objects.filter(visibility='PUBLIC', unlisted=False).order_by('-published')
    
    #only check one author's posts or all posts
    if author:
        posts = Post.objects.filter(author=author,unlisted=False).order_by('-published')
    else:
        posts = Post.objects.filter(unlisted=False).order_by('-published')

    for post in posts:
        if post.author == requester:    #my post
            result.append(post)
        elif post.visibility == 'PUBLIC':   #everyone can see's post
            result.append(post)
        elif post.visibility == 'FRIENDS':  #if friends then append this post
            if FriendshipViews.checkFriendship(post.author.id, requester.id):
                result.append(post)
        elif post.visibility == 'FOAF':     #friends of friends also can see
            if FriendshipViews.checkFriendship(post.author.id, requester.id):
                result.append(post)
            else:
                for friend in FriendshipViews.getAllFriends(post.author.id):
                    if FriendshipViews.checkFriendship(friend.friend_id, requester.id):
                        result.append(post)
        elif post.visibility == 'SERVERONLY':   #requires to be local friends
            if post.author.host == requester.host:
                result.append(post)
            print("SERVERONLY unimplemented.")
    return result

'''
    show a list of public posts, check visibility before display to user
'''
def ViewPublicPosts(request):
    form = PostNewForm(request.POST or None)
    if request.method == 'POST' and request.user.activated:
        try:
            if form.is_valid():
                form_data = form.cleaned_data
                form.cleaned_data['author'] = request.user
                newpost =Post.objects.create(**form.cleaned_data)
                form = PostNewForm()
            else:
                print(form.errors)
        except Exception as e:
            print(e)
    posts = getVisiblePosts(request.user)
    context = {
        'post_list': posts,
        'form': form,
    }

    return render(request, "posting/stream.html", context)

'''
    given a post_id show all its details, including comments
'''
def ViewPostDetails(request, post_id):
    post = Post.objects.get(id=post_id)

    comments = Comment.objects.filter(post=post)[:10]
    context = {
        'post': post,
        'comment_list': comments,
    }
    return render(request, "posting/post-details.html", context)

'''
    delete a specified post by post_id
'''
@login_required
def DeletePost(request, post_id):
    if request.user.activated:
        try:
            post = Post.objects.get(id=post_id)
            post.delete()
        except Exception as e:
            print(e)

    return HttpResponseRedirect(reverse('posting:view user posts', args=(request.user.id,)), {})

'''
    use POST to resend a form to update an existing post
'''
@login_required
def editPost(request, post_id):
    form = request.POST or None
    if request.method == 'POST' and request.user.activated:
        try:
            post = Post.objects.get(id=post_id)
            if form['title']:
                post.title = form['title']
            if form['content']:
                post.content = form['content']
            if form['visibility']:
                post.visibility = form['visibility']
            if form['contentType']:
                post.contentType = form['contentType']
            post.save()
        except Exception as e:
            print(e)
            return render(request, 'post/postDetail.html', {
                'error_message': "Failed to edit post.",
            })

    return HttpResponseRedirect(reverse('posting:view user posts', args=(request.user.id,)), {})

'''
    create a new comment under a specified post
'''
@login_required
def postCommentHandler(request, post_id, comment_id=None):
    post = Post.objects.get(id=post_id)
    if request.method in ['POST', 'PUT'] and request.user.activated:
        form = CommentForm(request.POST or None)
        context = {
            "query": "addComment",
            "success": None,
            "message": None,
        }
        if form.is_valid():
            form_data = form.cleaned_data
            form_data['user'] = request.user
            form_data['post'] = post
            comment = Comment(post=post, author=request.user,
                              comment=form_data['comment'])
            comment.save()
            context['success'] = True
            context['message'] = "Comment Added"
        else:
            print(form.errors)
            context['success'] = False
            context['message'] = "Comment not Allowed"

    return HttpResponseRedirect(reverse('posting:view post details', args=(post_id,)), context)


'''
    delete a specified comment by its comment_id
'''
@login_required
def deleteComment(request, post_id, comment_id=None):
    if request.user.activated:
        post = Post.objects.get(id=post_id)
        context = {
            "query": "deleteComment",
                "success": None,
                "message": None,
        }
        try:
            comment = Comment(id=comment_id)
            comment.delete()
            context['success'] = True
            context['message'] = "Comment deleted"
        except:
            context['success'] = False
            context['message'] = "Delete not Allowed"

    return HttpResponseRedirect(reverse('posting:view post details', args=(post_id,)), context)

'''
    show a specified author's posts, 10 posts each time
'''
def ViewUserPosts(request, author_id):
    author = User.objects.filter(id=author_id)[0]

    if request.method == 'GET':
        posts = getVisiblePosts(request.user, author)
        count = len(posts)
        #get from front-end or default
        size = 10
        origin = None
        next = None
        preivous = None

    context = {
        "query": "posts",
        "count": count,
        "size": size,
        "next": next,
        "previous": preivous,
        "posts": posts,
        "allowEdit":True,
    }
    
    return render(request, "posting/user-post-list.html", context)
