import os

from django.conf import settings
from django.db import models


class UploadFile(models.Model):
    file_name = models.CharField(max_length=300)
    uploaded_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="file_user",
    )

    # def __str__(self):
    #     return self.uploaded_on.date()


class CustomQuerySet:
    pass


class FileInDb(models.Model):
    file = models.FileField()
    file_id = models.OneToOneField(
        UploadFile,
        on_delete=models.CASCADE,
        related_name='file_in_db',
        primary_key=True,
    )
    #
    # def get_queryset(self):
    #     qs = CustomQuerySet(self.model)
    #     if self._db is not None:
    #         qs = qs.using(self._db)
    #     return qs

class FileOnDisk(models.Model):
    file = models.CharField(max_length=300)
    file_id = models.OneToOneField(
        UploadFile,
        on_delete=models.CASCADE,
        related_name="file_on_disk",
        primary_key=True
    )
