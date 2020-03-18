from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    #path('register/', views.create_author, name='create author'),
    #Visibility Private and Public 
    #TO Test: Friends and FOAF
    path('posts/', views.view_public_post, name='view public posts'), #OK GET 
    path('posts/<str:post_id>/', views.view_single_post, name='view single post'),#OK GET POST
    path('posts/<str:post_id>/comments/', views.handle_comments, name='handle comments'), #OK GET POST
    path('author/posts/', views.handle_auth_posts, name='handle authenticated posts'), #OK GET POST
    path('author/<str:author_id>/posts/', views.view_author_posts, name='view author posts'),#OK GET (POST Json)
    path('author/<str:author_id>/', views.ViewProfile, name='view profile'), #OK  GET (POST form)
    
    path('author/<str:author_id>/friends/', views.get_friendlist, name='get friend list'), #OK 
    path('author/<str:author1_id>/friends/<str:author2_id>/', views.check_friendship, name='check friendship'), #OK
    path('friendrequest/', views.make_friendRequest, name='make friend request'), #OK (POST)
]
