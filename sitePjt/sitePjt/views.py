from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import generic

@login_required
def home(request):
    #return render(request, "home.html",)
    if not request.user:
        redirect('/accounts/')
    return redirect('/' + request.user.username)