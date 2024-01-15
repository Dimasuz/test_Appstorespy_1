
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('regloginout.urls', namespace='regloginout')),
    path('', include('uploader.urls', namespace='uploader')),
    # for allauth
    path('accounts/', include('allauth.urls')),
    # for auth0
    path('', include('app_auth0.urls', namespace='app_auth0')),
    path('', include('social_django.urls')),
    # for django-silk
    path('silk/', include('silk.urls', namespace='silk')),
    # доступ к описанию проекта из API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
