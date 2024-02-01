import asyncio
import os.path
from datetime import datetime, timedelta

import aiofiles
from celery.result import AsyncResult
from django.conf import settings
from django.core.files import File
from django.http import FileResponse, Http404, JsonResponse
from drf_spectacular.utils import (OpenApiExample, OpenApiParameter,
                                   extend_schema)
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from test_appstorespy_1.settings import MAX_TIME_UPLOAD_FILE
from test_appstorespy_1.tasks import processing_file

from .models import UploadFile
from .serializers import FileUploadSerializer


async def upladed_file_save(file, file_name):
    async with aiofiles.open(file_name, "wb+") as f:
        uploaded_file = File(f)
        for chunk in file.chunks():
            await uploaded_file.write(chunk)
    return uploaded_file.name


async def handle_uploaded_file(file, file_path):
    task = asyncio.create_task(
        upladed_file_save(file, os.path.join(file_path, file.name))
    )
    await task
    # ограничим время загрузки файла
    stop_time = datetime.now() + timedelta(minutes=int(MAX_TIME_UPLOAD_FILE))
    while datetime.now() < stop_time:
        if task.done():
            return {
                "Status": True,
            }
        else:
            await asyncio.sleep(1)
    task.cancel()
    return {"Status": False, "error": "too long uploading file"}


@extend_schema(
    request=FileUploadSerializer,
    responses={201: FileUploadSerializer},
)
class FileUploadAPIView(APIView):
    """
    Класс для загрузки файла
    """

    # Загрузка файла методом POST

    parser_classes = (MultiPartParser, FormParser)
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse(
                {"Status": False, "Error": "Log in required"}, status=403
            )

        if "file" in request.FILES:
            file = request.FILES["file"]
            uploaded_file_path = os.path.join(settings.MEDIA_ROOT, "files_uploaded")
            uploaded_file = asyncio.run(handle_uploaded_file(file, uploaded_file_path))

            if uploaded_file["Status"]:
                request.data["file"] = file.name
                request.data["file_path"] = uploaded_file_path
                serializer = self.serializer_class(data=request.data)

                if serializer.is_valid():
                    uploaded_file_id = serializer.save().pk
                    return JsonResponse(
                        {"Status": True, "File_id": uploaded_file_id}, status=201
                    )
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            else:
                return JsonResponse(
                    {"Status": False, "File": uploaded_file["Result"]}, status=408
                )

        else:
            # return Response(status=status.HTTP_400_BAD_REQUEST)
            return JsonResponse({"Status": False}, status=400)


@extend_schema(
    request=FileUploadSerializer,
    responses={201: FileUploadSerializer},
)
class FileDownloadAPIView(APIView):
    """
    Класс для выгрузки файла
    """

    # Download file by method GET

    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse(
                {"Status": False, "Error": "Log in required"}, status=403
            )

        file_id = request.query_params.get("file_id", None)

        if file_id is not None:

            try:
                file = UploadFile.objects.all().filter(pk=file_id)[0]
            except IndexError as ex:
                return JsonResponse(
                    {"Status": False, "Error": "File_id not found."}, status=403
                )

            if file.user != request.user:
                return JsonResponse(
                    {"Status": False, "Error": "You try to get not yours file."},
                    status=403,
                )

            file_name = file.file
            file_path = file.file_path
            download_file = os.path.join(file_path, file_name)

            if os.path.exists(download_file):
                return FileResponse(
                    open(download_file, "rb"),
                    content_type="application/octet-stream",
                    as_attachment=True,
                )
            else:
                return JsonResponse(
                    {"Status": False, "Error": "File not found"}, status=400
                )

        return JsonResponse({"Status": False, "Error": "File_id required"}, status=400)


@extend_schema(
    request=FileUploadSerializer,
    responses={201: FileUploadSerializer},
)
class FileProcessingAPIView(APIView):
    """
    Класс для обработки файла
    """

    # Processing file by method GET
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = FileUploadSerializer

    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse(
                {"Status": False, "Error": "Log in required"}, status=403
            )

        file_id = request.query_params.get("file_id", None)

        if file_id is not None:
            try:
                file = UploadFile.objects.all().filter(pk=file_id)[0]
                file_name = file.file
                file_path = file.file_path
                # отправим файл на обработку в Celery
                async_result = processing_file.delay(os.path.join(file_path, file_name))
                return JsonResponse(
                    {
                        "Status": True,
                        "Task_id": async_result.task_id,
                    },
                    status=201,
                )
            except Exception as e:
                return e, Http404("File not found")

        return JsonResponse({"Status": False, "Error": "File_id required"}, status=400)


class CeleryStatus(APIView):
    """
    Класс для получения статуса отлооженных задач в Celery
    """

    # Получение сатуса задач Celery методом GET
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        task_id = request.query_params.get("task_id")
        if task_id:
            try:
                task = AsyncResult(task_id)
                task_status = task.status
                task_result = task.ready()
                return JsonResponse(
                    {"Status": task_status, "Result": task_result}, status=200
                )
            except Exception as err:
                return err

        return JsonResponse({"Status": False, "Error": "Task_id required"}, status=400)
