import asyncio
import os.path
from datetime import datetime, timedelta

import aiofiles

from celery.result import AsyncResult
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.http import JsonResponse, FileResponse, StreamingHttpResponse, HttpResponse
from drf_spectacular.utils import (OpenApiExample, OpenApiParameter,
                                   extend_schema)
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from test_appstorespy_1.settings import MAX_TIME_UPLOAD_FILE
from test_appstorespy_1.tasks import processing_file

from .models import UploadFile, FileInDb
from .serializers import UploadFileSerializer, FileOnDiskSerializer ,FileInDbSerializer


@extend_schema(
    request=UploadFileSerializer,
    responses={201: UploadFileSerializer},
)
class FileUploadToDbAPIView(APIView):

    """upload and download file to or from db"""

    # Upload file by method POST
    """POST"""

    # # save dirict to model
    # async def upladed_file_save(self, file, file_upload):
    #     file = FileInDb(file=file, file_id=file_upload).asave()
    #     # file = FileInDefDb(file=file, file_id=file_upload).asave(using='mongo_db')
    #     await file


    # save by serializer
    from asgiref.sync import sync_to_async
    @sync_to_async
    def upladed_file_save(self, file, file_upload):
        serializer_class = FileInDbSerializer
        data = {'file': file, 'file_id': file_upload.pk}
        serializer = serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()


    async def handle_uploaded_file(self, file, file_upload):
        task = asyncio.create_task(
            self.upladed_file_save(file, file_upload)
        )
        # await task
        # ограничим время загрузки файла
        stop_time = datetime.now() + timedelta(minutes=int(MAX_TIME_UPLOAD_FILE))
        while datetime.now() < stop_time:
            if task.done():
                return {'Status': True,}
            else:
                await asyncio.sleep(1)
        task.cancel()
        return {'Status': False, 'Error': 'Too long uploading file'}

    def post(self, request):

        if not request.user.is_authenticated:
            return JsonResponse(
                {'Status': False, 'Error': 'Log in required'}, status=403
            )

        if "file" in request.FILES:
            file = request.FILES["file"]

            data = {'file_name': file.name, 'user': request.user.pk, 'file_store': 'db'}
            serializer = UploadFileSerializer(data=data)
            if serializer.is_valid():
                file_upload = serializer.save()
            else:
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

            sync_mode = request.data.get('sync_mode', None)

            if sync_mode:
                # sync upload
                # # dirict to model
                # FileInDb(file=file, file_id=file_upload).save()
                # return JsonResponse({"Status": True, "File_id": file_upload.pk}, status=201)
                # by serializer
                serializer_class = FileInDbSerializer
                data = {'file': file, 'file_id': file_upload.pk}
                serializer = serializer_class(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse({"Status": True, "File_id": file_upload.pk}, status=201)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                # async upload
                uploaded_file = asyncio.run(self.handle_uploaded_file(file, file_upload))
                if uploaded_file['Status']:
                    return JsonResponse({"Status": True, "File_id": file_upload.pk}, status=201)
                else:
                    return JsonResponse(
                        {'Status': False, 'Error': 'File was not upload.'}, status=400
                    )

        else:
            return JsonResponse({'Status': False, 'Error': 'There is not "file" in the request.'}, status=400)


    # Download file by method GET
    """GET"""
    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403,)

        file_id = request.query_params.get("file_id", None)

        if file_id is not None:

            try:
                uploaded_file = UploadFile.objects.get(pk=file_id)
            except ObjectDoesNotExist as ex:
                return JsonResponse(
                    {"Status": False, "Error": "File not found."}, status=403
                )

            if uploaded_file.user != request.user:
                return JsonResponse(
                    {"Status": False, "Error": "You try to get not yours file."},
                    status=403,
                )

            try:
                download_file = FileInDb.objects.get(file_id=uploaded_file)
            except IndexError:
                return JsonResponse({"Status": False, "Error": "File_id not found."}, status=403, )

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

            response = FileResponse(download_file.file,
                    content_type='application/force-download',
                    as_attachment=True,)
            response['Content-Disposition'] = f'attachment; filename="{download_file.file.name}"'

            # if response.status_code == 200:
            #     uploaded_file.delete()

            return response

        return JsonResponse({"Status": False, "Error": "file_id is required"}, status=400)


@extend_schema(
    request=UploadFileSerializer,
    responses={201: UploadFileSerializer},
)
class FileUploadToDiskAPIView(APIView):
    """upload and download file to or from disk"""

    parser_classes = (MultiPartParser, FormParser)
    serializer_classes = (UploadFileSerializer, FileOnDiskSerializer)

    # Upload file by method POST
    """POST"""
    async def upladed_file_save(self, file, file_name):
        async with aiofiles.open(file_name, "wb+") as f:
            uploaded_file = File(f)
            for chunk in file.chunks():
                await uploaded_file.write(chunk)

    async def handle_uploaded_file(self, file, file_name):
        task = asyncio.create_task(
            self.upladed_file_save(file, file_name)
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
        return {"Status": False, "Error": "Too long uploading file."}

    def post(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse(
                {"Status": False, "Error": "Log in required."}, status=403
            )

        if "file" in request.FILES:
            file = request.FILES["file"]

            request.data["file_name"] = file.name
            request.data["user"] = request.user.pk
            request.data['file_store'] = 'disk'
            serializer = self.serializer_classes[0](data=request.data)

            if serializer.is_valid():
                upload_file = serializer.save()
            else:
                return JsonResponse(
                    {'Status': False, 'Errors': serializer.errors}, status=400
                )

            uploaded_file_path_name = os.path.join(settings.FILES_UPLOADED, upload_file.file_name)
            uploaded_file = asyncio.run(self.handle_uploaded_file(file, uploaded_file_path_name))

            if uploaded_file['Status']:
                data = {'file': uploaded_file_path_name,
                        'file_id': upload_file.pk,
                        }
                serializer = self.serializer_classes[1](data=data)

                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse(
                        {'Status': True, 'File_id': upload_file.pk}, status=201
                    )
                else:
                    return JsonResponse(
                        {'Status': False, 'Error': serializer.errors}, status=400
                    )

            else:
                return JsonResponse(
                    {'Status': False, 'Error': uploaded_file['Result']}, status=408
                )

        else:
            return JsonResponse({'Status': False, 'Error': 'There is not "file" in the request.'}, status=400)


    # Download file by method GET
    """GET"""
    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse(
                {"Status": False, "Error": "Log in required"}, status=403
            )

        file_id = request.query_params.get("file_id", None)

        if file_id is not None:

            try:
                uploaded_file = UploadFile.objects.get(pk=file_id)
            except ObjectDoesNotExist as ex:
                return JsonResponse(
                    {"Status": False, "Error": "File not found."}, status=403
                )

            if uploaded_file.user != request.user:
                return JsonResponse(
                    {"Status": False, "Error": "You try to get not yours file."},
                    status=403,
                )


            download_file = os.path.join(settings.FILES_UPLOADED, uploaded_file.file_name)

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

        return JsonResponse({"Status": False, "Error": "file_id is required"}, status=400)


@extend_schema(
    request=UploadFileSerializer,
    responses={201: UploadFileSerializer},
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

        # file_id = request.query_params.get("file_id", None)
        file_id = request.data.get('file_id', None)

        if file_id is not None:

            try:
                uploaded_file = UploadFile.objects.get(pk=file_id)
            except ObjectDoesNotExist as ex:
                return JsonResponse(
                    {"Status": False, "Error": "File not found."}, status=403
                )

            if uploaded_file.user != request.user:
                return JsonResponse({"Status": False, "Error": "You try to put not yours file."},
                    status=403, )

            # processing by Celery
            async_result = processing_file.delay(file_id)

            return JsonResponse({"Status": True,"Task_id": async_result.task_id,}, status=201,)

        else:
            return JsonResponse({"Status": False, "Error": "file_id is required"}, status=400)


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
    request=UploadFileSerializer,
    responses={200: UploadFileSerializer},
)
class FileDeleteAPIView(APIView):

    """DELETE"""
    def delete(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403,)

        file_id = request.data.get('file_id', None)

        if file_id is not None:

            try:
                uploaded_file = UploadFile.objects.get(pk=file_id)
            except ObjectDoesNotExist as ex:
                return JsonResponse(
                    {"Status": False, "Error": "File not found."}, status=403
                )

            if uploaded_file.user == request.user:
                files_deleted = uploaded_file.delete()
                return JsonResponse({"Status": True, "Files_deleted": files_deleted[1]['uploader.UploadFile']}, status=200)
            else:
                return JsonResponse(
                    {"Status": False, "Error": "You try to delete not yours file."},
                    status=403,
            )

        return JsonResponse({"Status": False, "Error": "file_id is required"}, status=400)