from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('service/', views.ViewHomePage, name='home page'),
    path('accounts/', include('accounts.urls')),
    path('service/', include('posting.urls')),
]
