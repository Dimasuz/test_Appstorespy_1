from rest_framework import serializers

from .models import FileInDb, FileOnDisk, UploadFile


class UploadFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadFile
        fields = (
            "file_store",
            "file_name",
            "uploaded_on",
            "user",
        )


class FileInDbSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileInDb
        fields = (
            "file",
            "file_id",
        )


class FileOnDiskSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileOnDisk
        fields = (
            "file",
            "file_id",
        )
