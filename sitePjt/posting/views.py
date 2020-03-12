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
from .models import Post, Comment


from .forms import PostNewForm, CommentForm
from .serializers import *
from .models import Post###, VisibleTo
from friendship import views as FriendshipViews

User = get_user_model()

#helper funciton

def getVisiblePosts(requester, author=None):
    result = []
    if requester.is_anonymous:
        return Post.objects.filter(visibility='PUBLIC',unlisted=False).order_by('-published')
    
    if author:
        posts = Post.objects.filter(author=author,unlisted=False).order_by('-published')
    else:
        posts = Post.objects.filter(unlisted=False).order_by('-published')

    for post in posts:
        if post.author == requester:
            result.append(post)
        elif post.visibility == 'PUBLIC':
            result.append(post)
        elif post.visibility == 'FRIENDS':
            if FriendshipViews.checkFriendship(post.author.id, requester.id):
                result.append(post)
        elif post.visibility == 'FOAF':
            if FriendshipViews.checkFriendship(post.author.id, requester.id):
                result.append(post)
            else:
                for friend in FriendshipViews.getAllFriends(post.author.id):
                    if FriendshipViews.checkFriendship(friend.id, requester.id):
                        result.append(post)
        elif post.visibility == 'SERVERONLY':
            if post.author.host == requester.host:
                result.append(post)
            print("SERVERONLY unimplemented.")
        #if request.user.id in post.visibleTo and (not post in post_list):
            #post_list.append(post)
    return result

def ViewPublicPosts(request):
    form = PostNewForm(request.POST or None)
    if request.method == 'POST':
        try:
            if form.is_valid():
                #form.save()
                form_data = form.cleaned_data
                form.cleaned_data['author'] = request.user
                newpost =Post.objects.create(**form.cleaned_data)
                ###if form_data['visibleTo']:
                ###    for friend in form_data['visibleTo']:
                ###        visibleTo = VisibleTo(post=newpost, author=friend)
                ###        visibleTo.save()
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
    
def ViewPostDetails(request, post_id):
    post = Post.objects.get(id=post_id)

    comments = Comment.objects.filter(post=post)[:10]
    context = {
        'post': post,
        'comment_list': comments,
    }
    return render(request, "posting/post-details.html", context)

@login_required
def DeletePost(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        post.delete()
    except Exception as e:
        print(e)

    return HttpResponseRedirect(reverse('posting:view user posts', args=(request.user.id,)), {})


@login_required
def editPost(request, post_id):
    form = request.POST or None
    if request.method == 'POST':
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

@login_required
def postCommentHandler(request, post_id, comment_id=None):
    post = Post.objects.get(id=post_id)
    if request.method in ['POST', 'PUT']:
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


@login_required
def deleteComment(request, post_id, comment_id=None):
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