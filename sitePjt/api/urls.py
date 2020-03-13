from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    #path('register/', views.create_author, name='create author'),
    path('posts/', views.view_public_post, name='view public posts'),
    path('posts/<str:post_id>/', views.view_single_post, name='view single post'),
    path('posts/<str:post_id>/comments/', views.handle_comments, name='handle comments'),
    path('author/posts/', views.view_auth_posts, name='view authenticated posts'),
    path('author/<str:author_id>/posts/', views.view_author_posts, name='view author posts'),
    path('author/<str:author_id>/', views.ViewProfile, name='view profile'),
]
