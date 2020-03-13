from datetime import datetime
import uuid,json
import base64
from posting.models import Post, Comment
from accounts.models import AuthorManager,Author
from rest_framework import status
from accounts.views import register_view,login_view
from django.test import TestCase,Client
from accounts.forms import UserCreationForm,UserProfileForm
from rest_framework.test import APITestCase, URLPatternsTestCase
from django.contrib.auth import get_user_model
from django.urls import include, path, reverse
from django.contrib.auth.models import User
from friendship.models import FriendRequest, Friendship
import unittest
from selenium import webdriver
from django.contrib.auth import get_user_model



'''
Test for Authors
'''
class TestUsers(TestCase):
    def set_up(self):
        author = Author.objects.create_user(email='test1@mail.com',displayName='yipu1',password='test1')
        author.save()


    def test_add_user_successful_or_not(self):
        self.set_up()
        authors = Author.objects.get(email='test1@mail.com')
        self.assertEqual(authors.email,'test1@mail.com')
        self.assertEqual(authors.displayName,'yipu1')  


    def test_login_user(self):
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
        url = "/accounts/login/"
        data = { "email":'test1@mail.com',"displayName":'yipu1',"password":'test1'}
        response = self.c.post(url, data,format='json')
        self.assertEqual(response.status_code, 302)
        data = { 'email': 'test@g.com','displayName': 'yipu1', 'password': '123'}
        self.c.login(displayName='yipu', password='123')

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
    
    def test_create_profile(self):
        self.set_up()
        author = Author.objects.get(email='test1@mail.com')
        author.displayName = 'test1'
        author.github ='http://github.com'
        author.bio ='bio.com'
        author.save()
        self.assertEqual(author.displayName,'test1')
        self.assertEqual(author.github,'http://github.com')
        self.assertEqual(author.bio,'bio.com')
    
    def test_update_profile(self):
        self.set_up()
        author = Author.objects.get(email='test1@mail.com')
        form = UserProfileForm({'displayName':'new', 'bio':'http://new.com', 'github':'http://new.com'})
        self.assertTrue(form.is_valid())
        author.displayName = form.cleaned_data['displayName']
        author.bio = form.cleaned_data['bio']
        author.github = form.cleaned_data['github']
        self.assertEqual(author.displayName,'new')
        self.assertEqual(author.github,'http://new.com')
        self.assertEqual(author.bio,'http://new.com')


    def test_create_profile_with_non_existed_author(self):
        self.c=Client()
        self.user = Author.objects.create_user(email='test1@mail.com',displayName='yipu1', password='test1')
        self.author = Author.objects.get(email=self.user.email)
        url = '/accounts/author/profile' + str(self.author.id) + '/'
        response = self.c.get(url)
        self.assertEqual(response.status_code, 404)

     

'''
    Test cases for Posting 
'''
class TestPosts(TestCase):
    def setUp(self):
        self.c=Client()
        self.user = Author.objects.create_user( email='test1@mail.com',displayName='yipu1', password='test1')
        self.author = Author.objects.get(user_id=self.user.id)
        self.c.login(displayName='yipu1', password='test1')
        post = Post.objects.create(title="Test1", author_id=self.author.id)
        self.assertEqual(post.author_id, self.author.id)

    # The test we can creat a private post which doesnt show at public list.
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
    
    #The test for posting a public post.
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
    
    #The test for updating a post.
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
    
    #The test for deleting a post.
    def delete_post(self):
        self.c=Client()
        postID = Post.objects.all()[1].id
        url='/post/'+str(postID) 
        respons = self.c.delete(url)
        self.assertEqual(respons.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(),2)

    #The test add and delete comments with posts
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



'''
    Friend request test cases
''' 
class TestFriend(TestCase):
    def set_up_friendship(self):
        author_a = Author.objects.create_user(email="1@g.com",displayName="author",password="123")
        author_b = Author.objects.create_user(email="2@g.com",displayName="friend",password="124")
        Friendship.objects.create(author=self.author_a, friend=self.author_b)
        Friendship.objects.create(author=self.author_b, friend=self.author_a)
        
    def set_up_author(self): 
        author_a = Author.objects.create_user(email="1@g.com",displayName="author",password="123")
        author_b = Author.objects.create_user(email="2@g.com",displayName="friend",password="124")

    #Test friend for creating friendship and friendrequst. test if we can get the friendship between two users.
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

    #Test the friendrequest models
    def FriendRequest(self):
        self.author_a = Author.objects.create_user(email="1@g.com",displayName="author",password="123")
        self.author_b = Author.objects.create_user(email="2@g.com",displayName="friend",password="124")
        FriendRequest.objects.create(author=self.author_a, friend=self.author_b)
        friend_a = FriendRequest.objects.get(author=self.author_a.id)
        self.assertEqual(friend_a.author.displayName, "author")
        friend_b = FriendRequest.objects.get(author=self.author_a.id)
        self.assertEqual(friend_b.friend.displayName, "friend")
    
    def test_send_friend_request(self):
        a = Author.objects.create_user(email="1@g.com",displayName="author",password="123")
        b = Author.objects.create_user(email="2@g.com",displayName="friend",password="124")
        request = FriendRequest.objects.create(author_from=a, author_to= b)
        friendship = True
        try:
            Friendship.objects.get(author_a=a, author_b=b)
        except Friendship.DoesNotExist:
            friendship=False
        self.assertFalse(friendship)
        #pending state, no such author_a and author_b in friendship
    

    

   