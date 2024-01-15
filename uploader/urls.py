from django.urls import path

from uploader.views import FileUploadAPIView, UploadView

app_name = 'uploader'
urlpatterns = [
    path('api/v1/file/upload/', FileUploadAPIView.as_view(), name='file_upload'),
    path('file/upload-web/', UploadView.as_view(), name='file_upload_web'),
]
