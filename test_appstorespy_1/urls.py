from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)

from test_appstorespy_1.settings import API_VERTION
from uploader.views import CeleryStatus

api_vertion = API_VERTION

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"api/{api_vertion}/", include("regloginout.urls", namespace="regloginout")),
    path(f"api/{api_vertion}/", include("uploader.urls", namespace="uploader")),
    path(
        f"api/{api_vertion}/celery_status/",
        CeleryStatus.as_view(),
        name="celery_status",
    ),
    # for allauth
    path("accounts/", include("allauth.urls")),
    # for auth0
    path("", include("app_auth0.urls", namespace="app_auth0")),
    path("", include("social_django.urls")),
    # for django-silk
    path("silk/", include("silk.urls", namespace="silk")),
    # доступ к описанию проекта из API
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
