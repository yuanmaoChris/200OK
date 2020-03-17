from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls import url
from . import views
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='200OK API')

urlpatterns = [
    path('', views.ViewHomePage, name='home page'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('posting.urls')),
    path('', include('friendship.urls')),
    path('service/', include('api.urls')),
    path(r'swagger-docs/', schema_view),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
