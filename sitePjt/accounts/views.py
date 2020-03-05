from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from .models import profile, friendRequest
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout
)

from .forms import UserLoginForm, UserProfileForm, UserCreationForm
from .models import Author

#auth
def login_view(request):
    next = request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        print(form.cleaned_data)
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        if user:
            login(request, user)
        else:
            print("user does not exist")
        if next:
            return redirect(next)
        return redirect('/service/posts/')

    context = {
        'form': form,
    }
    return render(request,"accounts/login.html",context)

def register_view(request,backend='django.contrib.auth.backends.ModelBackend'):
    next = request.GET.get('next')
<<<<<<< HEAD
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()
        new_user = authenticate(username=user.username, password=password)
        login(request, user,backend='django.contrib.auth.backends.ModelBackend')
        if next:
            return redirect(next)
        return redirect('/')

=======
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            new_user = authenticate(email=email, password=password)
            login(request, new_user)
            if next:
                return redirect(next)
            return redirect('/service/posts/')
    else:
        form = UserCreationForm()
>>>>>>> yipu
    context = {
        'form': form,
    }
    return render(request,"accounts/signup.html",context)

def logout_view(request):
    logout(request)
<<<<<<< HEAD
    return redirect('/')

#get users list & followers list & friends list & private list (include friends and friends of friends)
def users_list(request):
    users = User.objects.exclude(username=request.user)
    requests = friendRequest.objects.filter(send_to=request.user)
    friends=request.user.profile.friends.all()
    private_set=set()
    for friend in friends:
        private_set.add(friend)
        frineds_of_friend=friend.profile.friends.all()
        for ffriend in frineds_of_friend:
            private_set.add(ffriend)
    context={
        'users': users,
        'requests': requests,
        'friends': friends,
        'private_set': private_set
    }
    return render(request,"home.html",context)

#------------------friend relationship functions-------------------------#

#equivalent to follow while pending request
def send_friend_request(request,id):
    if request.user.is_authenticated():
        user=get_object_or_404(User,id=id)
        frequest, created = friendRequest.objects.get_or_create(send_from=request.user,send_to=user)
        return HttpResponseRedirect('/users')

#equivalent to unfollow
def cancel_friend_request(request,id):
    if request.user.is_authenticated():
        user=get_object_or_404(User,id=id)
        frequest = friendRequest.objects.filter(send_from=request.user,send_to=user).first()
        frequest.delete()
        return HttpResponseRedirect('/users')

#be friend
def accept_friend_request(request,id):
    send_from=get_object_or_404(User,id=id)
    frequest = friendRequest.objects.filter(send_from=send_from,send_to=request.user).first()
    userA=frequest.send_to
    userB=send_from
    userA.profile.friends.add(userB.profile)
    userB.profile.friends.add(userA.profile)
    frequest.delete()
    return HttpResponseRedirect('/users')

#equivalent to decline follow
def delete_friend_request(request,id):
    send_from=get_object_or_404(User,id=id)
    frequest = friendRequest.objects.filter(send_from=send_from,send_to=request.user).first()
    frequest.delete()
    return HttpResponseRedirect('/users')

#un-befriend
def remove_friend(request,id):
    to_remove=User.objects.get(id=id)
    request.user.profile.friends.remove(to_remove)
    return HttpResponseRedirect('/users')

#-------------------------------------------------------------#
=======
    return redirect('/accounts/login/')


def profile_view(request):
    form = UserProfileForm(request.GET or None)

    context = {
        'form': form,
    }
    return render(request, "accounts/myProfile.html", context)
>>>>>>> yipu
