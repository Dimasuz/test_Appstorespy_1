from django.urls import path

from test_appstorespy_1.settings import API_VERTION
from uploader.views import (FileDeleteAPIView, FileDownloadAPIView,
                            FileProcessingAPIView, FileUploadAPIView)

api_vertion = API_VERTION

app_name = "uploader"

urlpatterns = [
    path("file/upload/", FileUploadAPIView.as_view(), name="file_upload"),
    path("file/download/", FileDownloadAPIView.as_view(), name="file_download"),
    path("file/processing/", FileProcessingAPIView.as_view(), name="file_processing"),
    path("file/delete/", FileDeleteAPIView.as_view(), name="file_delete"),
]
