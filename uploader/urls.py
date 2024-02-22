from django.urls import path

from test_appstorespy_1.settings import API_VERTION
from uploader.views import FileUploadToDiskAPIView, FileProcessingAPIView, FileUploadToDbAPIView, FileDeleteAPIView

api_vertion = API_VERTION

app_name = "uploader"

urlpatterns = [
    path("file/disk/upload/", FileUploadToDiskAPIView.as_view(), name="file_disk_upload"),
    path("file/disk/download/", FileUploadToDiskAPIView.as_view(), name="file_disk_download"),
    path("file/db/upload/", FileUploadToDbAPIView.as_view(), name="file_db_upload"),
    path("file/db/download/", FileUploadToDbAPIView.as_view(), name="file_db_download"),
    path("file/processing/", FileProcessingAPIView.as_view(), name="file_processing"),
    path("file/delete/", FileDeleteAPIView.as_view(), name="file_delete"),
]
