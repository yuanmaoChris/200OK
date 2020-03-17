from django.urls import path
from . import views

app_name = 'friendship'

urlpatterns = [
    path('author/<str:author_a>friends/<str:author_b>/', views.checkFriendship, name='check friendship'),
    path('author/<str:author_id>/friends/', views.getFriendsList, name='get friends list'),
    path('friendrequest/', views.sendRequest, name='friend request'),
    path('friendrequest/accept/', views.handleRequest, name='handle request'),
    path('friendrequest/unfriend/', views.deleteFriend, name='delete friend'),
    path('friendrequest/<str:author_id>/', views.ViewFriendsRequest, name='view friend request'),
    
]