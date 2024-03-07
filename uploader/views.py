import asyncio
import os.path
from contextlib import suppress
from datetime import datetime, timedelta

import aiofiles
from celery.result import AsyncResult
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.http import (FileResponse, JsonResponse, HttpResponse, StreamingHttpResponse)
from drf_spectacular.utils import (OpenApiExample, OpenApiParameter, extend_schema, inline_serializer, OpenApiResponse)
from rest_framework import status, serializers
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from test_appstorespy_1.settings import MAX_TIME_UPLOAD_FILE
from test_appstorespy_1.tasks import processing_file

from .models import FileInDb, FileOnDisk, UploadFile
from .serializers import (FileInDbSerializer, FileOnDiskSerializer, UploadFileSerializer)


@extend_schema(
    request=UploadFileSerializer,
    responses={201: inline_serializer(
            name="UploadFile",
            fields={"Status": serializers.BooleanField(), "File_id": serializers.CharField(),},
                    ),
    },
)
class FileUploadAPIView(APIView):
    """Upload file"""

    parser_classes = (MultiPartParser, FormParser)
    serializer_classes = (
        UploadFileSerializer,
        FileInDbSerializer,
        FileOnDiskSerializer,
    )

    # Upload file by method POST
    """POST"""

    async def upladed_file_save(self, file, file_upload):
        if file_upload.file_store == "db":
            file = FileInDb(file=file, file_id=file_upload).asave()
            # file = FileInDefDb(file=file, file_id=file_upload).asave(using='mongo_db')
        elif file_upload.file_store == "disk":
            file_path = os.path.join(settings.FILES_UPLOADED, file_upload.file_name)
            async with aiofiles.open(file_path, "wb+") as f:
                uploaded_file = File(f)
                for chunk in file.chunks():
                    await uploaded_file.write(chunk)
            file = FileOnDisk(file=file_path, file_id=file_upload).asave()
        await file

    async def handle_uploaded_file(self, file, file_upload):
        task = asyncio.create_task(self.upladed_file_save(file, file_upload))
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
        return {"Status": False, "Error": "UPLOAD_TIMED_OUT"}

    def post(self, request):

        if not request.user.is_authenticated:
            return JsonResponse(
                {"Status": False, "Error": "Log in required"}, status=403
            )

        if "file" in request.FILES:
            file = request.FILES["file"]
        else:
            return JsonResponse(
                {"Status": False, "Error": 'There is not "file" in the request.'},
                status=400,
            )

        if request.data.get("file_store", "db") not in settings.FILE_STORE:
            return JsonResponse(
                {"Status": False, "Error": 'Wrong "file_store" parameter.'}, status=400
            )

        request.data["file_name"] = file.name
        request.data["user"] = request.user.pk
        serializer = self.serializer_classes[0](data=request.data)
        if serializer.is_valid():
            file_upload = serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get("sync_mode", False):
            if file_upload.file_store == "disk":
                file_path = os.path.join(settings.FILES_UPLOADED, file_upload.file_name)
                with open(file_path, "wb+") as f:
                    uploaded_file = File(f)
                    for chunk in file.chunks():
                        uploaded_file.write(chunk)
                data = {
                    "file": file_path,
                    "file_id": file_upload.pk,
                }
                serializer = self.serializer_classes[2](data=data)
            else:
                data = {"file": file, "file_id": file_upload.pk}
                serializer = self.serializer_classes[1](data=data)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse(
                    {"Status": True, "File_id": file_upload.pk}, status=201
                )
            else:
                file_upload.delete()
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            # async upload
            uploaded_file = asyncio.run(self.handle_uploaded_file(file, file_upload))

            if uploaded_file["Status"]:
                return JsonResponse(
                    {"Status": True, "File_id": file_upload.pk}, status=201
                )
            else:
                file_upload.delete()
                return JsonResponse(uploaded_file, status=400)



@extend_schema(
    parameters=[
        OpenApiParameter(name="file_id", required=True, type=str),
    ],
    description="Download file with id",
    responses={
        (201, 'application/octet-stream'): inline_serializer(
           name='FileDownloadResponse',
           fields={
               'file': serializers.FileField(),
           },
       ),
    }
)
class FileDownloadAPIView(APIView):
    """
    Class for download file
    """

    # Download file by method GET
    """GET"""

    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse(
                {"Status": False, "Error": "Log in required"}, status=403
            )

        file_id = request.query_params.get("file_id", False)

        if file_id:

            try:
                uploaded_file = UploadFile.objects.get(pk=file_id)

                if uploaded_file.user != request.user:
                    return JsonResponse(
                        {"Status": False, "Error": "You try to get not yours file."},
                        status=403,
                    )

                if uploaded_file.file_store == "db":
                    download_file = FileInDb.objects.get(file_id=uploaded_file)

                    # response = HttpResponse(download_file.file,
                    #                         # content_type="text/csv",
                    #                         # headers={"Content-Disposition": f'attachment;
                    #                                    filename={file_name}'},
                    #                         )

                    # response = StreamingHttpResponse(download_file.file,
                    #                           content_type="text/csv",
                    #                           headers={"Content-Disposition": f'attachment;
                    #                                    filename={download_file.file.name}'},
                    #                           )

                    response = FileResponse(
                        download_file.file,
                        content_type="application/octet-stream",
                        as_attachment=True,
                    )
                    response["Content-Disposition"] = (
                        f'attachment; filename="{download_file.file.name}"'
                    )

                    return response

                elif uploaded_file.file_store == "disk":
                    download_file = FileOnDisk.objects.get(file_id=uploaded_file).file

                    if os.path.exists(download_file):
                        return FileResponse(
                            open(download_file, "rb"),
                            content_type="application/octet-stream",
                            as_attachment=True,
                        )
                    else:
                        return JsonResponse(
                            {"Status": False, "Error": "File not found"}, status=404
                        )

                else:
                    return JsonResponse(
                        {"Status": False, "Error": "File not found."}, status=404
                    )

            except ObjectDoesNotExist as ex:
                return JsonResponse(
                    {"Status": False, "Error": "File not found."}, status=404
                )

        return JsonResponse(
            {"Status": False, "Error": "file_id is required"}, status=400
        )


@extend_schema(
    parameters=[
        OpenApiParameter(name="file_id", required=True, type=str),
    ],
    description="Pricessing file with id",
    responses={
        (201, 'application/json'): inline_serializer(
           name='FileProcessingResponse',
           fields={
                "Status": serializers.BooleanField(),
                "Task_id": serializers.CharField(),
           },
       ),
    },
)
class FileProcessingAPIView(APIView):
    """
    Класс для обработки файла
    """

    # Processing file by method PUT
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = UploadFileSerializer

    def put(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse(
                {"Status": False, "Error": "Log in required"}, status=403
            )

        file_id = request.data.get("file_id", None)

        if file_id is not None:

            try:
                uploaded_file = UploadFile.objects.get(pk=file_id)
            except ObjectDoesNotExist as ex:
                return JsonResponse(
                    {"Status": False, "Error": "File not found."}, status=404
                )

            if uploaded_file.user != request.user:
                return JsonResponse(
                    {"Status": False, "Error": "You try to put not yours file."},
                    status=403,
                )

            # processing by Celery
            async_result = processing_file.delay(file_id)

            return JsonResponse(
                {
                    "Status": True,
                    "Task_id": async_result.task_id,
                },
                status=201,
            )

        else:
            return JsonResponse(
                {"Status": False, "Error": "file_id is required"}, status=400
            )


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


@extend_schema(
    parameters=[OpenApiParameter(name="file_id", required=True, type=str),],
    description="Delete file with id",
    responses={(200, 'application/json'): inline_serializer(
            name='FileDeleteResponse',
            fields={
                'Status': serializers.BooleanField(),
                'Files_deleted': serializers.IntegerField(),
                }
            ),
    }
)
class FileDeleteAPIView(APIView):
    """DELETE"""

    def delete(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse(
                {"Status": False, "Error": "Log in required"},
                status=403,
            )

        file_id = request.data.get("file_id", None)

        if file_id is not None:

            try:
                uploaded_file = UploadFile.objects.get(pk=file_id)
                if uploaded_file.file_store == "db":
                    file = FileInDb.objects.get(file_id=uploaded_file)
                    file_path = file.file.path
                elif uploaded_file.file_store == "disk":
                    file = FileOnDisk.objects.get(file_id=uploaded_file)
                    file_path = file.file
                else:
                    file_path = None
            except ObjectDoesNotExist as ex:
                return JsonResponse(
                    {"Status": False, "Error": "File not found."}, status=404
                )

            if uploaded_file.user == request.user:
                files_deleted = uploaded_file.delete()
                if file_path:
                    with suppress(OSError):
                        os.remove(file_path)

                return JsonResponse(
                    {
                        "Status": True,
                        "Files_deleted": files_deleted[1]["uploader.UploadFile"],
                    },
                    status=200,
                )
            else:
                return JsonResponse(
                    {"Status": False, "Error": "You try to delete not yours file."},
                    status=403,
                )

        return JsonResponse(
            {"Status": False, "Error": "file_id is required"}, status=400
        )
