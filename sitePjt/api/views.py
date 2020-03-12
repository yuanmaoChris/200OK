from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseServerError

from posting.models import Post, Comment
from .serializers import PostSerializer, AuthorSerializer
Author = get_user_model()
'''
class ListUsers(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        usernames = [user.username for user in User.objects.all()]
        return Response(usernames)
'''

@api_view()
def hello_world(request):
    return Response({"message": "Hello, world!"})


@api_view()
def ViewPublicPosts(request):
    if request.method == 'GET':
        try:
            posts = Post.objects.filter(visibility='PUBLIC').order_by('-published')
            serializer = PostSerializer(posts, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(e)
        return HttpResponseNotFound()
    return HttpResponseBadRequest()

@api_view()
def ViewProfile(request, author_id):

    if request.method == 'GET':
        try:
            author = Author.objects.get(id=author_id)
            if author:
                serializer = AuthorSerializer(author)
                return Response(serializer.data)
            else:
                return HttpResponseNotFound(b"User Not found")
        except Exception as e:
            print(e)
            return HttpResponseServerError()
    else:  
        return HttpResponseBadRequest()


@api_view()
def ViewComment(request, post_id):

    if request.method == 'GET':
        try:
            post = Post.objects.get(id=post_id)
            if post:
                serializer = PostSerializer(post)
                return Response(serializer.data)
            else:
                return HttpResponseNotFound(b"User Not found")
        except Exception as e:
            print(e)
            return HttpResponseServerError()
    else:
        return HttpResponseBadRequest()











'''
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
'''
