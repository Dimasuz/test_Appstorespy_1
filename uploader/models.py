import os

from django.conf import settings
from django.db import models


class UploadFile(models.Model):
    file = models.CharField(max_length=300)
    file_path = models.CharField(max_length=300)
    uploaded_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="file_user",
    )

    # def __str__(self):
    #     return self.uploaded_on.date()
