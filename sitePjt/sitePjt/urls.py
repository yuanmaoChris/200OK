from django.contrib import admin
from django.urls import path, include

<<<<<<< HEAD
from .views import home

from accounts.views import login_view, register_view, logout_view, users_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home),
    path('accounts/login/',login_view),
    path('accounts/register/', register_view),
    path('accounts/logout/', logout_view),
    path('users/',users_list)
=======
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('service/', views.ViewHomePage, name='home page'),
    path('accounts/', include('accounts.urls')),
    path('service/', include('posting.urls')),
>>>>>>> yipu
]
