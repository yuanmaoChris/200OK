from django.urls import path
from . import views

app_name = 'posting'

urlpatterns = [
     path('<str:username>/', views.MyHomeView.as_view(), name='home page'),
     path('<str:username>/newPost/', views.createPost, name='create post'),
     path('<str:username>/myPost/', views.myPostView.as_view(), name='view my post'),
     path('<str:username>/postResult/', views.post, name='post result'),
     path('<str:username>/myPost/postDetail/<str:pk>/', views.postDetailView.as_view(), name='post detail'),
     path('<str:username>/myPost/postDetail/<str:pk>/editPost',
         views.editPost, name='edit post'),
     path('<str:username>/myPost/postDetail/<str:pk>/deletePost',
         views.deletePost, name='delete post'),
     path('test/post/', views.post_list),
]
