import uuid
import pytest

from regloginout.models import User, ConfirmEmailToken

# from rest_framework.authtoken.models import Token
# from model_bakery import baker
# from django.contrib.auth import authenticate, login, logout


URL_BASE = 'http://127.0.0.1:8000/api/v1/'

# фикстура для api-client'а
@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


# фикстура для регистрации и получения ConfirmEmailToken
@pytest.fixture
def register_user(api_client):
    url_view = 'user/register/'
    url = URL_BASE + url_view
    num = str(uuid.uuid4())
    email = f'email_{num}@mail.ru'
    password = f'Password_{num}'
    data = {'first_name': f'first_name_{num}',
            'last_name': f'last_name_{num}',
            'email': email,
            'password': password,
            }
    response = api_client.post(url,
                           data=data,
                           )
    user = User.objects.all().filter(email=email).get()
    conform_token = ConfirmEmailToken.objects.filter(user_id=user.id).values_list('key', flat=True).get()
    return api_client, user, conform_token, password

# @pytest.fixture
# def create_user_active():
#    def make_user(**kwargs):
#        test_name = str(uuid.uuid4())
#        kwargs['password'] = '123password'
#        kwargs['email'] = '123@example.com'
#        kwargs['is_active'] = True
#        return User.objects.create_user(**kwargs)
#    return make_user

# @pytest.fixture()
# def create_token():
#     token, _ = Token.objects.get_or_create(user=user)
#     return token.key


# # фикстура логина пользователя
# @pytest.fixture()
# def user_create(api_client):
#     password = str(uuid.uuid4())
#     user = baker.make(User, is_active=True, password=password, email=password+'@test.com')
#     # token, _ = Token.objects.get_or_create(user=user)
#     return api_client, user, password

