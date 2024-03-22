import os
import time
from datetime import datetime
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse

from test_appstorespy_1.celery import app
from uploader.models import UploadFile


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


# task for processing file
@app.task
def processing_file(file_path):

    time.sleep(10)

    with open(file_path, "rb+") as f:
        f.seek(0, 2)
        f.write(f"\ncelery_{datetime.now()}".encode())

    return file_path
