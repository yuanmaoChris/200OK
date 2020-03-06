from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from datetime import datetime
User = get_user_model()

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from .models import Post, Comment
from .forms import PostForm, PostNewForm, CommentForm
from .serializers import *
from .models import Post

def ViewPublicPosts(request):
    public_posts = Post.objects.filter(visibility='PUBLIC').order_by('-pub_date')[:10]
    form = PostNewForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            #form.save()
            form_data = form.cleaned_data
            form.cleaned_data['author'] = request.user
            Post.objects.create(**form.cleaned_data)
            form = PostNewForm()
        else:
            print(form.errors)
    
    context = {
        'public_post_list': public_posts,
        'form': form,
    }

    return render(request, "posting/publicPosts.html", context)

def DeletePost(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        post.delete()
    except Exception as e:
        print(e)

    return redirect('/service/posts/')

def ViewPostDetails(request, post_id):
    post = Post.objects.get(id=post_id)

    if request.method == "DELETE":
        try:
            post.delete()
        except Exception as e:
            print(e)
        finally:
            return redirect('/service/posts/')

    comments = Comment.objects.filter(post=post)[:10]
    context = {
        'post': post,
        'comment_list': comments,
    }
    return render(request, "posting/postDetails.html", context)

def postCommentHandler(request, post_id, comment_id=None):
    post = Post.objects.get(id=post_id)
    if request.method == 'DELETE':
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

    elif request.method in ['POST', 'PUT']:
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
            comment = Comment(post=post, author=request.user, content=form_data['content'])
            comment.save()
            context['success'] = True
            context['message'] = "Comment Added"
        else:
            print(form.errors)
            context['success'] = False
            context['message'] = "Comment not Allowed"
            

    return HttpResponseRedirect(reverse('posting:view post details', args=(post_id,)), context)


def ViewUserPosts(request, author):

    return "User posts"

# Create your views here.












def post(request, username):
    try:
        user = get_object_or_404(User, username=username)
    except:
        return render(request, 'post/creatingPost.html', {
            'error_message': "Failed to create a new post, user info does not match.",
        })

    try:
        content = request.POST.get('content')
    except KeyError:
        return render(request, 'post/creatingPost.html', {
            'error_message': "Failed to create a new post, no content found.",
        })
    else:
        post = Post(content=content, author=request.user)
        #Check length <= max content length(200)
        post.save()

    return HttpResponseRedirect(reverse('posting:home page', args=(username,)))


class myPostView(generic.ListView):
    template_name = 'posting/myPost.html'
    context_object_name = 'my_post_list'
    user = None

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        return Post.objects.filter(author=user.id)


class MyHomeView(generic.ListView):
    template_name = 'posting/home.html'
    context_object_name = 'latest_post_list'

    def get_queryset(self):
        return Post.objects.filter(visibility='PUBL').order_by('-pub_date')[:10]
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['follow_list'] = Follow.objects.filter(follower_id=self.request.user)
        return context


class postDetailView(generic.DetailView):
    model = Post
    template_name = 'posting/postDetail.html'


def postDetailsView(request, pk):
    form = PostForm(request.POST or None)
    if form.is_valid():
        form.save()
    
    context = {
        'form': form
    }
    return render(request, 'posting/post_detail.html', context)

def editPost(request, username, pk):
    try:
        user = get_object_or_404(User, username=username)
    except:
        return render(request, 'post/postDetail.html', {
            'error_message': "Failed to edit post, user info does not match.",
        })

    try:
        content = request.POST['content']
        visibility = request.POST['visibility']
    except KeyError:
        return render(request, 'post/postDetail.html', {
            'error_message': "Failed to edit post.",
        })
    else:
        Post.objects.filter(id=pk).update(content=content, visibility=visibility, pub_date=now())
        #Check length <= max content length(200)

    return HttpResponseRedirect(reverse('posting:view my post', args=(username,)))


@api_view(['GET', 'POST'])
def post_list(request):
    if request.method == 'GET':
        data = Post.objects.all()

        serializer = PostSerializer(
            data, context={'request': request}, many=True)

        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
def post_detail(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = PostSerializer(
            post, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
