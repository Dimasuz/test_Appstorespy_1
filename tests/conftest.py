import time
import pytest
from rest_framework.authtoken.models import Token
from regloginout.models import User, ConfirmEmailToken
from model_bakery import baker

URL_BASE = 'http://127.0.0.1:8000/api/v1/'

# фикстура для api-client'а
@pytest.fixture
def client():
    from rest_framework.test import APIClient
    return APIClient()


# фикстура для регистрации и получения ConfirmEmailToken
@pytest.fixture
def register_user(client):
    url_view = 'user/register/'
    url = URL_BASE + url_view
    num = time.time()
    email = f'email_{num}@mail.ru'
    password = f'Password_{num}'
    data = {'first_name': f'first_name_{num}',
            'last_name': f'last_name_{num}',
            'email': email,
            'password': password,
            }
    response = client.post(url,
                           data=data,
                           )
    print(response.status_code)
    print(response.json())
    user_id = User.objects.all().filter(email=email).values_list('id', flat=True).get()
    conform_token = ConfirmEmailToken.objects.filter(user_id=user_id).values_list('key', flat=True).get()
    user = {'status_code': response.status_code,
            'status': response.json()['Status'],
            # 'task_id': response.json()['task_id'],
            'email': email,
            'password': password,
            'conform_token': conform_token,
            }
    return user


# # фикстура для наполенения базы данных
# @pytest.fixture
# def fill_base(client):
#     users = []
#     for i in range(4):
#         user = baker.make(User, is_active=True)
#         token, _ = Token.objects.get_or_create(user=user)
#         users.append({'id': user.id, 'email': user.email, 'token': token})
#     return users


# фикстура логина пользователя
@pytest.fixture()
def user_create_login(client):
    user = baker.make(User, is_active=True)
    token, _ = Token.objects.get_or_create(user=user)
    return user, token