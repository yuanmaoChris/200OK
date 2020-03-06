from django.urls import path
from . import views

app_name = 'posting'

urlpatterns = [
    path('posts/', views.ViewPublicPosts, name='view public posts'),
    path('posts/<str:post_id>', views.ViewPostDetails, name='view post details'),
    path('posts/<str:post_id>/delete/', views.DeletePost, name='delete post'),
    #path('posts/<str:post_id>/comments/', views.ViewPostDetails, name='view comments'),
    path('posts/<str:post_id>/comments/', views.postCommentHandler, name='comment events'),
    path('author/<str:user_id>/posts/', views.ViewUserPosts, name='view user posts'),
]
