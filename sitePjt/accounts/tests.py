from datetime import datetime
import uuid,json
import base64
from posting.models import Post, Comment
from .models import AuthorManager,Author
from rest_framework import status
from .views import register_view,login_view
from django.test import TestCase,Client
from .forms import UserCreationForm
from rest_framework.test import APITestCase, URLPatternsTestCase
from django.contrib.auth import get_user_model
from django.urls import include, path, reverse
from django.contrib.auth.models import User
from friendship.models import FriendRequest, Friendship
import unittest
from selenium import webdriver
from django.contrib.auth import get_user_model




# Create your models here.
#test the user exisit 
class TestUsers(TestCase):
    def test_user(self):
        self.c=Client()
        try:
            user1= Author.objects.get(email='test1@mail.com',displayName='yipu1',password='test1')
            self.assertEqual(user1.email,'test1@mail.com')
            self.assertEqual(user1.displayName,'yipu1')
            self.assertEqual(user1.password,'test1')
        except:
                pass
        self.assertEqual(Author.objects.count(), 0)
        url = "/accounts/register/"
        data = { 'email': 'test@g.com','displayName': 'yipu1', 'password': '123'}
        response = self.c.post(url, data,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.author=Author.objects.create_user('test1@mail.com','yipu1', 'test1')
        #test login
        url = "/accounts/login/"
        data = { "email":'test1@mail.com',"displayName":'yipu1',"password":'test1'}
        response = self.c.post(url, data,format='json')
        self.assertEqual(response.status_code, 302)
        data = { 'email': 'test@g.com','displayName': 'yipu1', 'password': '123'}
        self.c.login(displayName='yipu', password='123')
    #test get a wrong id with profile 
    def test_profile(self):
        self.c=Client()
        self.user = Author.objects.create_user(email='test1@mail.com',displayName='yipu1', password='test1')
        self.author = Author.objects.get(email=self.user.email)
        url = '/accounts/author/profile' + str(self.author.id) + '/'
        response = self.c.get(url)
        self.assertEqual(response.status_code, 404)
    
    #test tge signup page work       
    def test_signup_response(self):
        self.c=Client()
        data = {
            'email':'122122@test.com',
            'displayName':'yipu1',
            'password':'a1234'
            }
        url = '/accounts/register'
        response=self.c.get(url,data)
        self.assertEqual(response.status_code,301)


#test the post 
class TestPosts(TestCase):
    def setUp(self):
        self.c=Client()
        self.user = Author.objects.create_user( email='test1@mail.com',displayName='yipu1', password='test1')
        self.author = Author.objects.get(user_id=self.user.id)
        self.c.login(displayName='yipu1', password='test1')
        post = Post.objects.create(title="Test1", author_id=self.author.id)
        self.assertEqual(post.author_id, self.author.id)

    # test we can creat a private post which doesnt show at public list.

    def  private_post(self):
        self.c=Client()
        url='/post'

        data = {"title":"private",
                "contentType":'text',
                "content":"sample private",
                "categories":"None",
                "author":self.author.id,
                "visibility":'PRIVATE'
        }
        response = self.c.post(url,data,format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().title, 'private')
        get = self.c.get(url)
        self.assertEqual(get.status_code,status.HTTP_200_OK)
        self.assertEqual(get.data.get('posts'),[])
    
    def public_post(self):
        self.c=Client()
        url='/post'

        data = {"title":"public",
                "contentType":'text',
                "content":"sample public",
                "categories":"None",
                "author":self.author.id,
                "visibility":'PUBLIC'
        }
    
        response = self.c.post(url,data,format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().title, 'public')
        get = self.c.get(url)
        self.assertEqual(get.status_code,status.HTTP_200_OK)
        self.assertEqual(get.data.get('posts'),[])

    def update_post(self):
        self.c=Client()
        url= "/accounts/register"
        data= {'email': 'test@g.com','displayName': 'u1', 'password': '123321', }
        user= self.c.post(url, data, format='json')
        self.assertEqual(Post.objects.count(), 0)
        url = "/posts/"
        data=data['user']
        user= user.data
        data = {'title': "test"}
        response = self.c.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['title'], "test")
        self.assertEqual(response.data['author'], user['url'])
    
    def delete_post(self):
        self.c=Client()
        postID = Post.objects.all()[1].id
        url='/post/'+str(postID) 
        respons = self.c.delete(url)
        self.assertEqual(respons.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(),2)

    #test add and delete comments with posts
    def comments_with_posts(self):
        postID = Post.objects.all()[1].id
        default = uuid.uuid4()
        time = str(datetime.now())
        comment = {
            "id":str(default),
            "author": {
                "id": str(self.author.id),
                "displayName": "yipu1",
                "url":str(self.author.url),
                },
            "content-type":'text/plain',
            "comment":"test",
            "published":time
            }
        url = '/posts/' + str(postID) + '/' + 'comments/'
        response = self.client.post(url,comment,format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        respons_del= self.c.delete(url)
        self.assertEqual(respons_del.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(),2)
        
#test friend for creating friendship and friendrequst. test if we can get the friendship between two users.
class TestFriend(TestCase):
    def creat_friendship(self):        
        self.author_a = Author.objects.create_user(email="1@g.com",displayName="author",password="123")
        self.author_b = Author.objects.create_user(email="2@g.com",displayName="friend",password="124")
        Friendship.objects.create(author=self.author_a, friend=self.author_b)
        Friendship.objects.create(author=self.author_b, friend=self.author_a)
        friend_a= Friendship.objects.get(author=self.author_a.id)
        friend_b= Friendship.objects.get(author=self.author_b.id)
        self.assertEqual(friend_a.author.displayName, "author")
        self.assertEqual(friend_b.author.displayName, "friend")
        self.assertEqual(friend_a.friend.displayName, "author")
        self.assertEqual(friend_b.friend.displayName, "friend")

#test the friendrequest models
    def FriendRequest(self):
        self.author_a = Author.objects.create_user(email="1@g.com",displayName="author",password="123")
        self.author_b = Author.objects.create_user(email="2@g.com",displayName="friend",password="124")
        FriendRequests.objects.create(author=self.author_a, friend=self.author_b)
        friend_a = FriendRequests.objects.get(author=self.author_a.id)
        self.assertEqual(friend_a.author.displayName, "author")
        friend_b = FriendRequests.objects.get(author=self.author_a.id)
        self.assertEqual(friend_b.friend.displayName, "friend")


    

   
        
  
