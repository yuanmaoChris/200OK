from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('register/', views.register_view, name="sign up"),
    path('logout/', views.logout_view, name="logout"),
    path('author/profile/<str:author_id>/', views.ProfileView.as_view(), name='view profile'),
]
