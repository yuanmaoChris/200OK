from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    #path('register/', views.create_author, name='create author'),
    path('posts/', views.view_public_post, name='view public posts'), #OK
    path('posts/<str:post_id>/', views.view_single_post, name='view single post'),#OK
    path('posts/<str:post_id>/comments/', views.handle_comments, name='handle comments'), #OK
    path('author/posts/', views.handle_auth_posts, name='handle authenticated posts'), #OK
    path('author/<str:author_id>/posts/', views.view_author_posts, name='view author posts'),#OK
    path('author/<str:author_id>/', views.ViewProfile, name='view profile'), #OK
    path('author/<str:author_id>/friends/', views.get_friendlist, name='get friend list'),
    path('author/<str:author1_id>/friends/<str:author2_id>/', views.check_friendship, name='check friendship'),
    path('friendrequest/', views.make_friendRequest, name='make friend request'),
]
