import asyncio
import aiofiles
from django.http import JsonResponse
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from .serializers import FileUploadSerializer

from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import UploadFile



async def handle_uploaded_file(f):
    async with aiofiles.open(f.name, 'wb+') as destination:
        for chunk in f.chunks(1):
            await destination.write(chunk)

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
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        serializer = self.serializer_class(data=request.data)

        if 'file' in request.FILES or serializer.is_valid():
            asyncio.run(handle_uploaded_file(request.FILES['file']))
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=FileUploadSerializer,
    responses={201: FileUploadSerializer},
)
class UploadView(CreateView):
    model = UploadFile
    serializer_class = FileUploadSerializer
    fields = ['file', ]
    success_url = reverse_lazy('file_upload_web')
    template_name = 'uploader/upload_form.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['file'] = UploadFile.objects.all()
        return context
