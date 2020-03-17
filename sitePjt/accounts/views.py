from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout
)
from .forms import UserLoginForm, UserProfileForm, UserCreationForm
from .models import Author
from posting import views as PostingView

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
            print("user does not exist")
            return render(request, "accounts/login.html", {'form': UserLoginForm()})
        if next:
            return redirect(next)
        return redirect('/posts/')
    else:
        form = UserLoginForm()
        context = {
            'form': form,
        }
        return render(request, "accounts/login.html", context)


'''
    registe new user by creating and saving a UserCreationForm
'''


def register_view(request):
    next = request.GET.get('next')
    if request.user.is_authenticated:
        print("authenticated!")
        return redirect('/posts/')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            new_user = authenticate(request, email=email, password=password)
            login(request, new_user)
            if next:
                return redirect(next)
            return redirect('/posts/')
    else:
        form = UserCreationForm()
        context = {
            'form': form,
        }
        return render(request, "accounts/signup.html", context)


'''
    simply logout and jump back to login page
'''


def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')

'''
    given an author id to find the specified user's information
'''
@login_required
def profile_view(request, author_id):
    form = request.POST
    if request.method == "POST":
        print(form)
        Author.objects.filter(id=author_id).update(
            displayName=form['displayName'],
            bio=form['bio'],
            github=form['github'],
        )

    author = Author.objects.filter(id=author_id)[0]
    posts_list = []
    '''
        current user is browsing others profile page, so only show allowed posts
    '''
    if request.user.id != author_id:
        posts_list = PostingView.getVisiblePosts(request.user, author)

    context = {
        'displayName': author.displayName,
        'avatar': author.avatar,
        'github': author.github,
        'url': author.url,
        'host': author.host,
        'bio': author.bio,
        'email': author.email,
        'id': author.id,
        'joined_date': author.date_joined,
        'post_list': posts_list,
    }

    return render(request, "accounts/profile.html", context)
