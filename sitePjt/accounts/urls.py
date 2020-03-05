from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view),
    path('register/', views.register_view, name="sign up"),
    path('logout/', views.logout_view),
    path('myProfile/', views.profile_view),
    
]
