import os
import time
from datetime import datetime
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from test_appstorespy_1.celery import app
from uploader.models import FileInDb, FileOnDisk, UploadFile


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
def processing_file(file_id):
    time.sleep(5)

    file = UploadFile.objects.all().filter(pk=file_id)[0]

    if file.__class__ == FileInDb:
        file = FileInDb.objects.filter(file_id__pk=file_id)[0]
        file_path = file.file.path
    elif file.__class__ == FileOnDisk:


    with open(file_path, "rb+") as f:
        f.seek(0, 2)
        f.write(f'\n"celery_"{datetime.now()}'.encode())

    # with NamedTemporaryFile("w+b", prefix=file.file.name, suffix='') as f:
    #     f.write(file.file)
    #     f.write(f'\n"celery_"{datetime.now()}')
    #     f.seek(0)
    # o.__class__.__name__
    # processing_file = os.path.join(settings.FILES_UPLOADED, file.file)
    # with open(file, 'r+') as f:
    #     f.seek(0, 2)
    #     f.write(f'\n"celery_"{datetime.now()}')

    # return file


