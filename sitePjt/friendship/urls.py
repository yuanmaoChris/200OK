from django.urls import path
from . import views

app_name = 'friendship'

urlpatterns = [
    path('author/<str:author_id>/friends/', views.GetFriendsListView.as_view(), name='get friends list'),
    path('friendrequest/', views.SendFriendRequestView.as_view(), name='friend request'),
    path('friendrequest/accept/', views.HandleRequestView.as_view(), name='handle request'),
    path('friendrequest/unfriend/', views.DeleteFriendView.as_view(), name='delete friend'),
    path('friendrequest/<str:author_id>/', views.FriendsRequestView.as_view(), name='view friend request'),
]
