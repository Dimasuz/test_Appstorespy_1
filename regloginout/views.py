# from django.shortcuts import render

# from celery.result import AsyncResult
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
# from django.core.exceptions import ValidationError
# from django.core.validators import URLValidator
# from django.db import IntegrityError
# from django.db.models import Q, Sum, F
from django.http import JsonResponse
# from requests import get
from rest_framework.authtoken.models import Token
# from rest_framework.generics import ListAPIView
# from rest_framework.response import Response
from rest_framework.views import APIView
# from rest_framework import viewsets
# from ujson import loads as load_json
# from yaml import load as load_yaml, Loader

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from regloginout.models import ConfirmEmailToken
from regloginout.serializers import UserSerializer
from regloginout.signals import new_user_registered
# from netology_pd_diplom.tasks import task_print

# decorators @extend_schema is for OPEN API

@extend_schema(
    request=UserSerializer,
    responses={201: UserSerializer},
)
class RegisterAccount(APIView):
    """
    User registration
    """
    def post(self, request, *args, **kwargs):

        # проверяем обязательные аргументы
        if {'first_name', 'last_name', 'email', 'password'}.issubset(request.data):
            # проверяем пароль на сложность
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                # проверяем данные для уникальности имени пользователя
                request.data._mutable = True
                request.data.update({})
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    # сохраняем пользователя
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    # # для применения celery возвращаем task задачи для возможности контроля ее выполнения
                    # send_mail = new_user_registered.send(sender=self.__class__, user_id=user.id)
                    # return JsonResponse({'Status': True, 'task_id': send_mail[0][1]})
                    token = new_user_registered.send(sender=self.__class__, user_id=user.id)

                    # return JsonResponse({'Status': True})

                    try:
                        JsonResponse(token)
                    except Exception as e:
                        token = token[0][1]

                    return JsonResponse({'Status': True, 'token': token})

                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


@extend_schema(
    request=UserSerializer,
    responses={201: UserSerializer},
)
class ConfirmAccount(APIView):
    """
    Класс для подтверждения почтового адреса
    """
    # Регистрация методом POST
    def post(self, request, *args, **kwargs):

        # проверяем обязательные аргументы
        if {'email', 'token'}.issubset(request.data):

            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
                                                     key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': 'Неправильно указан токен или email'})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

#
# @extend_schema(
#     request=UserSerializer,
#     responses={201: UserSerializer},
# )
# class AccountDetails(APIView):
#     """
#     Класс для работы с данными пользователя
#     """
#
#     # получить данные
#     def get(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
#
#         serializer = UserSerializer(request.user)
#         return Response(serializer.data)
#
#     # Редактирование методом POST
#     def post(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
#         # проверяем обязательные аргументы
#         if 'password' in request.data:
#             errors = {}
#             # проверяем пароль на сложность
#             try:
#                 validate_password(request.data['password'])
#             except Exception as password_error:
#                 error_array = []
#                 # noinspection PyTypeChecker
#                 for item in password_error:
#                     error_array.append(item)
#                 return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
#             else:
#                 request.user.set_password(request.data['password'])
#
#         # проверяем остальные данные
#         user_serializer = UserSerializer(request.user, data=request.data, partial=True)
#         if user_serializer.is_valid():
#             user_serializer.save()
#             return JsonResponse({'Status': True})
#         else:
#             return JsonResponse({'Status': False, 'Errors': user_serializer.errors})
#
#
@extend_schema(
    request=UserSerializer,
    responses={201: UserSerializer},
)
class LoginAccount(APIView):
    """
    Класс для авторизации и логина пользователей
    """
    # Авторизация методом POST
    def post(self, request, *args, **kwargs):

        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])

            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)
                    login(request, user)
                    return JsonResponse({'Status': True, 'Token': token.key})

            return JsonResponse({'Status': False, 'Errors': 'Не удалось авторизовать'})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class LogoutAccount(APIView):
    """
    Класс для логаута пользователей
    """
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        logout(request)

        return JsonResponse({'Status': True})




#
#
# # для полчения статуса задач в celery добавим view class
# class CeleryStatus(APIView):
#     """
#     Класс для получения статуса отлооженных задач в Celery
#     """
#
#     # получить статус задачи в celery
#     def get(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
#
#         task_id = request.query_params.get('task_id')
#         if task_id:
#             task_result = AsyncResult(task_id)
#             result = task_result.status
#             return JsonResponse({'status': result}, status=200)