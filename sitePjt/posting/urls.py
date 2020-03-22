from django.urls import path
from . import views
from .api import views as APIviews
app_name = 'posting'

urlpatterns = [
    path('posts/', APIviews.ViewPublicPosts.as_view(), name='view public posts'),
    path('posts/<str:post_id>/', APIviews.ViewPostDetails.as_view(), name='view post details'),
    path('posts/<str:post_id>/delete/', APIviews.DeletePost.as_view(), name='delete post'),
    path('posts/<str:post_id>/edit/', APIviews.EditPost.as_view(), name='edit post'),
    path('posts/<str:post_id>/comments/', APIviews.CommentHandler.as_view(), name='comment handler'),
    path('posts/<str:post_id>/comments/<str:comment_id>/', APIviews.CommentHandler.as_view(), name='comment handler'),
    path('author/<str:author_id>/posts/', APIviews.ViewUserPosts.as_view(), name='view user posts'),
]
