from django.urls import path
from . import views

app_name = 'posting'

urlpatterns = [

    path('posts/', views.ViewPublicPosts, name='view public posts'),
    path('posts/<str:post_id>', views.ViewPostDetails, name='view post details'),
    path('posts/<str:post_id>/delete/', views.DeletePost, name='delete post'),
    path('posts/<str:post_id>/comments/', views.ViewPostDetails, name='view comments'),
    path('posts/<str:post_id>/comments/newComment', views.AddPostComment, name='add comment'),
    path('posts/<str:post_id>/comments/deleteComment/<str:comment_id>', views.DeletePostComment, name='delete comment'),
    path('author/<str:user_id>/posts/', views.ViewUserPosts, name='view user posts'),

    #  path('newPost/', views.createPost, name='new post'),
    #  path('Posts/<str:pk>', views.postDetailView.as_view(), name='post detail'),
    #  path('<str:username>/myPost/', views.myPostView.as_view(), name='view my post'),
    #  path('<str:username>/postResult/', views.post, name='post result'),
    #  #path('<str:username>/myPost/postDetail/<str:pk>/', views.postDetailView.as_view(), name='post detail'),
    #  path('<str:username>/myPost/postDetail/<str:pk>/editPost',
    #      views.editPost, name='edit post'),
    #  path('<str:username>/myPost/postDetail/<str:pk>/deletePost',
    #      views.deletePost, name='delete post'),
    #  path('test/post/', views.post_list),
]
