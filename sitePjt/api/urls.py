from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('posts/', views.ViewPublicPosts, name='view public posts'),
    path('author/<str:author_id>', views.ViewProfile, name='view profile'),
    path('helloworld/', views.hello_world, name='hello world'),
]
