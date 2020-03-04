from django.shortcuts import render, redirect

from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout
)

from .forms import UserLoginForm, UserProfileForm
from .models import Author
from .admin import UserCreationForm

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

def register_view(request):
    next = request.GET.get('next')
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
    context = {
        'form': form,
    }
    return render(request,"accounts/signup.html",context)

def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')


def profile_view(request):
    form = UserProfileForm(request.GET or None)

    context = {
        'form': form,
    }
    return render(request, "accounts/myProfile.html", context)
