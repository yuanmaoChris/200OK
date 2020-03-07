from django.urls import path
from . import views

app_name = 'friendship'

urlpatterns = [
    path('author/<str:author_a>friends/<str:author_b>/', views.checkFriendship, name='check friendship'),
    path('author/<str:author_a>friends/', views.getFriendsList, name='get friends list'),
    path('friendrequest/', views.sendRequest, name='friend request'),
    path('friendrequest/accept/', views.acceptRequest, name='accept request'),
    path('friendrequest/<str:author_id>/', views.ViewFriendsRequest, name='view friend request'),
]
