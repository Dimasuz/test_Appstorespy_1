import os
import time
from datetime import datetime

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
        [email],
    )
    msg.send()


# таска для обработки файла
@app.task
def processing_file(file):
    time.sleep(10)
    # with open(file, 'r+') as f:
    #     f.seek(0, 2)
    #     f.write(f'\n"celery_"{datetime.now()}')
    return file


