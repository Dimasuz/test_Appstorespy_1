from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from test_appstorespy_1.celery import app


# формирование и отправка писем перенесены из signals.py в tasks.py для применения в celery
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


# тестовая таска
@app.task
def task_print(pr, t):
    import time
    print(pr)
    time.sleep(t)
    print(pr)
    return pr