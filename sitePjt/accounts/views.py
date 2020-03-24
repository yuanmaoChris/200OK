from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError, HttpResponseNotAllowed, HttpResponseForbidden
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout
)
from .forms import UserLoginForm, UserProfileForm, UserCreationForm
from .models import Author
from .permissions import IsActivated, IsActivatedOrReadOnly
from posting import views as PostingView
from friendship.models import Friend
import requests
from .serializers import AuthorSerializer
'''
    check if input email/password is valid and the user actually exist before login
'''

def login_view(request):
    next = request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        if user:
            login(request, user)
        else:
            print("returned None")
        if next:
            return redirect(next)
        return redirect('/posts/')

    context = {
        'form': form,
    }
    return render(request, "accounts/login.html", context)

def register_view(request):
    '''
    registe new user by creating and saving a UserCreationForm
    '''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            new_user = authenticate(email=email, password=password)
            login(request, new_user)
            return redirect('/posts/')
    else:
        form = UserCreationForm()
    return render(request, "accounts/signup.html", context={'form': form})


def logout_view(request):
    '''
    simply logout and jump back to login page
    '''
    logout(request)
    return redirect('/accounts/login/')


#@login_required
# def profile_view(request, author_id):
#     '''
#     given an author id to find the specified user's information
#     '''
#     form = request.POST
#     if request.method == "POST":
#         print(form)
#         Author.objects.filter(id=author_id).update(
#             displayName=form['displayName'],
#             bio=form['bio'],
#             github=form['github'],
#         )
#         Friend.objects.filter(friend_id=author_id).update(
#             friend_displayName=form['displayName']
#         )

#     author = Author.objects.filter(id=author_id)[0]
#     posts_list = []
#     '''
#         current user is browsing others profile page, so only show allowed posts
#     '''
#     if request.user.id != author_id:
#         posts_list = PostingView.getVisiblePosts(request.user, author)

#     context = {
#         'displayName': author.displayName,
#         'avatar': author.avatar,
#         'github': author.github,
#         'url': author.url,
#         'host': author.host,
#         'bio': author.bio,
#         'email': author.email,
#         'id': author.id,
#         'joined_date': author.date_joined,
#         'post_list': posts_list,
#     }

#     return render(request, "accounts/profile.html", context)


class ProfileView(APIView):
    """
    View to a detail of author profile and its posts list in the system.

    * Requires token authentication.
    * Only authenticated authors are able to access this view.
    """
    #authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsActivatedOrReadOnly]

    def get(self, request, author_id, format=None):
        '''
            current user is browsing others profile page, so only show allowed posts
        '''
        try:
            author = Author.objects.filter(id=author_id)
            if not author.exists():
                author = getNodeAuthor(author_id)
                if author == None:
                    return HttpResponseNotFound("Author Profile Not Found.")
            else:    
                author = Author.objects.get(id=author_id)
            posts_list = []
            #Viewing other's profile. Get all visible posts of that author.
            if request.user.id != author_id:
                posts_list = PostingView.getVisiblePosts(request.user, author)
            context = {
                'author': author,
                'post_list': posts_list,
            }
            return render(request, "accounts/profile.html", context)
        except Exception as e:
            return HttpResponseServerError(e)

    def post(self, request, author_id, format=None):
        try:
            author = Author.objects.filter(id=author_id)
            if not author.exists():
                return HttpResponseNotFound("Author Profile Not Found.")
            form = request.POST
            Author.objects.filter(id=author_id).update(
                displayName=form['displayName'],
                bio=form['bio'],
                github=form['github'],
            )
            Friend.objects.filter(friend_id=author_id).update(
                friend_displayName=form['displayName']
            )
            author = Author.objects.get(id=author_id)
            posts_list = []
            #Viewing other's profile. Get all visible posts of that author.
            if request.user.id != author_id:
                posts_list = PostingView.getVisiblePosts(request.user, author)
            context = {
                'author': author,
                'post_list': posts_list,
            }
            return render(request, "accounts/profile.html", context)
        except Exception as e:
            return HttpResponseServerError(e)

def getNodeAuthor(author_id,Node=None):
    user = 'cmput404w20t05@gmail.com'
    pwd = 'demo'
    #Try request from remote server
    url = 'https://cmput404w20t05.herokuapp.com/api/author/{}'.format(str(author_id))
    response = requests.get(url, auth=(user, pwd))
    author = None
    #TODO: Issues Author Serializers is not working here
    if response.status_code == 200:
        remote_author = response.json()
        author = getJsonDecodeAuthor(remote_author)
    return author

def findAuthorIdFromUrl(url):
    if url[-1] == '/':
        idx = url[:-1].rindex('/')
        return url[idx+1:-1]
    else:
        idx = url.rindex('/')
        return url[idx+1:]

def getJsonDecodeAuthor(remote_author):
    author = Author()
    author.id = findAuthorIdFromUrl(remote_author['url'])
    author.url = remote_author['url'] if 'url' in remote_author.keys() else 'None'
    author.displayName = remote_author['displayName'] if 'displayName' in remote_author.keys() else 'None'
    author.bio =  remote_author['bio'] if 'bio' in remote_author.keys() else 'None'
    author.host = remote_author['host'] if 'host' in remote_author.keys() else 'None'
    author.github = remote_author['github'] if 'github' in remote_author.keys() else 'None'
    author.date_joined = remote_author['date_joined'] if 'date_joined' in remote_author.keys() else 'None'
    author.last_login = remote_author['last_login'] if 'last_login' in remote_author.keys() else 'None'
    return author