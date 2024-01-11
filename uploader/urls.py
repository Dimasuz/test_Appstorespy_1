from django.urls import path

from uploader.views import FileUploadAPIView

app_name = 'uploader'
urlpatterns = [
    path('file/upload/', FileUploadAPIView.as_view(), name='file_upload'),
]
