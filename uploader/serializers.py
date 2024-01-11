from rest_framework import serializers
from .models import UploadFile

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadFile
        fields = ('file', 'uploaded_on',)