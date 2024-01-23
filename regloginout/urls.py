from django.urls import path
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm

from regloginout.views import RegisterAccount, LoginAccount, LogoutAccount, ConfirmAccount, \
    UserDetails, CeleryStatus, DeleteAccount

app_name = 'regloginout'

api_vertion = 'v1'

urlpatterns = [
    path(f'api/{api_vertion}/user/register/', RegisterAccount.as_view(), name='user_register'),
    path(f'api/{api_vertion}/user/register/confirm/', ConfirmAccount.as_view(), name='user_confirm'),
    path(f'api/{api_vertion}/user/login/', LoginAccount.as_view(), name='user_login'),
    path(f'api/{api_vertion}/user/details/', UserDetails.as_view(), name='user_details'),
    path(f'api/{api_vertion}/user/logout/', LogoutAccount.as_view(), name='user_logout'),
    path(f'api/{api_vertion}/user/delete/', DeleteAccount.as_view(), name='user_delete'),
    path(f'api/{api_vertion}/user/celery_status/', CeleryStatus.as_view(), name='user_celery_status'),
    path(f'api/{api_vertion}/user/password_reset/', reset_password_request_token, name='password-reset'),
    path(f'api/{api_vertion}/user/password_reset/confirm/', reset_password_confirm, name='password-reset-confirm'),
]


