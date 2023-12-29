from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver, Signal
# from django.http import JsonResponse
from django_rest_passwordreset.signals import reset_password_token_created

from regloginout.models import ConfirmEmailToken, User
# from test_appstorespy_1.tasks import send_email

# new_user_registered = Signal(
#     providing_args=['user_id'],
# )
#
# new_order = Signal(
#     providing_args=['user_id'],
# )
# изменения в связи с новой версией Django
new_user_registered: Signal = Signal('user_id')

new_order: Signal  = Signal('user_id')

new_contact: Signal  = Signal('user_id')

# формирование и отправка писем перенесены в tasks.py для применения в celery

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    """
    Отправляем письмо с токеном для сброса пароля
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param kwargs:
    :return:
    """
    # send an e-mail to the user

    # async_result = send_email.delay(reset_password_token.user.email,
    #                                 f"Password Reset Token for {reset_password_token.user}",
    #                                 reset_password_token.key
    #                                 )
    #
    # return async_result.task_id


    msg = EmailMultiAlternatives(
        # title:
        f"Password Reset Token for {reset_password_token.user}",
        # message:
        reset_password_token.key,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [reset_password_token.user.email]
    )
    # msg.send()
    return {'email': reset_password_token.user.email, 'user': reset_password_token.user,
            'token': reset_password_token.key}


@receiver(new_user_registered)
def new_user_registered_signal(user_id, **kwargs):
    """
    отправляем письмо с подтрердждением почты
    """
    # send an e-mail to the user
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)

    # async_result = send_email.delay(token.user.email,
    #                                 f"Password Reset Token for {token.user.email}",
    #                                 token.key
    #                                 )
    #
    # return async_result.task_id

    msg = EmailMultiAlternatives(
        # title:
        f"Password Reset Token for {token.user.email}",
        # message:
        token.key,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [token.user.email]
    )

    try:
        msg.send()
    except Exception as e:
        status_mail = e.strerror
    else:
        status_mail = True
    token = {'token': token.key, 'status_mail': status_mail}

    return token
