from django.http import JsonResponse
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from .serializers import FileUploadSerializer


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

        if serializer.is_valid():
            # you can access the file like this from serializer
            # uploaded_file = serializer.validated_data["file"]
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )





# from django.views.generic.edit import CreateView
# from django.urls import reverse_lazy
# from .models import Upload
#
# class UploadView(CreateView):
#     model = Upload
#     fields = ['upload_file', ]
#     success_url = reverse_lazy('file_upload')
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['file'] = Upload.objects.all()
#         return context


