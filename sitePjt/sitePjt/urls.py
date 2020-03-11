from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from . import views
from friendship.views import FriendRequestViewSet,FriendshipViewSet
####
from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'friendrequest', FriendRequestViewSet)
router.register(r'friendship', FriendshipViewSet)

####


urlpatterns = [
    path('admin/', admin.site.urls),
    path('service/', views.ViewHomePage, name='home page'),
    path('accounts/', include('accounts.urls')),
    path('service/', include('posting.urls')),
    path('service/', include('friendship.urls')),
    ##############################
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    ##############################
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
