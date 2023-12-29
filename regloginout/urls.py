from django.urls import path
# from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm
from regloginout.views import RegisterAccount, LoginAccount, LogoutAccount, ConfirmAccount #, CeleryStatus

app_name = 'regloginout'
urlpatterns = [
    path('user/register/', RegisterAccount.as_view(), name='user-register'),
    path('user/register/confirm/', ConfirmAccount.as_view(), name='user-register-confirm'),
    path('user/login/', LoginAccount.as_view(), name='user-login'),
    path('user/logout/', LogoutAccount.as_view(), name='user-login'),

    # path('user/password_reset/', reset_password_request_token, name='password-reset'),
    # path('user/password_reset/confirm/', reset_password_confirm, name='password-reset-confirm'),
    # path('status/', CeleryStatus.as_view(), name='status'),
]
