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

from .models import Post
from .serializers import *



from .models import Post, Follow
# Create your views here.
def createPost(request, username):
    return render(request, 'posting/creatingPost.html', {})

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
        post = Post(content=content, user_id=request.user)
        #Check length <= max content length(200)
        post.save()

    return HttpResponseRedirect(reverse('posting:home page', args=(username,)))


def deletePost(request, username, pk):
    try:
        user = get_object_or_404(User, username=username)
    except:
        return render(request, 'postting/myPost.html', {
            'error_message': "Failed to create a new post, user info does not match.",
        })
    else:
        post = Post.objects.get(id=pk)
        post.delete()

    return HttpResponseRedirect(reverse('posting:view my post', args=(username,)))


class myPostView(generic.ListView):
    template_name = 'posting/myPost.html'
    context_object_name = 'my_post_list'
    user = None

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        return Post.objects.filter(user_id=user.id)


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
