from django.urls import path
# from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm
from regloginout.views import RegisterAccount, LoginAccount, LogoutAccount, ConfirmAccount, \
    UserDetails, CeleryStatus

app_name = 'regloginout'

urlpatterns = [
    path('api/v1/user/register/', RegisterAccount.as_view(), name='user_register'),
    path('api/v1/user/register/confirm/', ConfirmAccount.as_view(), name='user_confirm'),
    path('api/v1/user/login/', LoginAccount.as_view(), name='user_login'),
    path('api/v1/user/details/', UserDetails.as_view(), name='user_details'),
    path('api/v1/user/logout/', LogoutAccount.as_view(), name='user_logout'),
    path('api/v1/user/celery_status/', CeleryStatus.as_view(), name='user_celery_status'),


    # path('user/password_reset/', reset_password_request_token, name='password-reset'),
    # path('user/password_reset/confirm/', reset_password_confirm, name='password-reset-confirm'),

]


