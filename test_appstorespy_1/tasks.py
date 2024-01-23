from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from test_appstorespy_1.celery import app


# формирование и отправка писем для применения в celery
@app.task
def send_email(email, title, massage):

    msg = EmailMultiAlternatives(
        # title:
        title,
        # message:
        massage,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [email]
    )
    msg.send()
