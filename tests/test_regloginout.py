import pytest
import warnings

from django.shortcuts import get_object_or_404

from rest_framework.authtoken.models import Token
from .conftest import URL_BASE
from regloginout.models import User

warnings.filterwarnings(action="ignore")

pytestmark = pytest.mark.django_db

# URL_BASE = 'http://127.0.0.1:8000/api/v1/'

def test_example():
    assert True, "Just test example"


# check /api/v1/user/register

def test_user_register(register_user):
    api_client, user, confirm_token, _, response = register_user
    assert user
    assert confirm_token
    assert response.json()['Status'] == True
    assert response.json()['task_id']


# check /api/v1/user/register/confirm
def test_register_confirm(register_confirm):
    api_client, _, _, response = register_confirm

    assert response.json()['Status'] == True
    assert response.status_code == 200


# check /api/v1/user/login
def test_user_login(register_confirm):
    api_client, user, password, _ = register_confirm

    # user/login
    url_view = 'user/login/'
    url = URL_BASE + url_view
    data = {'email': user.email,
            'password': password,
            }
    response = api_client.post(url,
                           data=data,
                           )
    print(response.json())
    assert response.status_code == 200
    assert response.json()['Token']
    token_from_db, _ = Token.objects.get_or_create(user=user)
    token = response.json()['Token']
    assert token == token_from_db.key

# user/logout
def test_user_logout(login):
    api_client, _, token = login
    url_view = 'user/logout/'
    url = URL_BASE + url_view
    headers = {'Authorization': f"Token {token}"}
    response = api_client.post(url,
                          headers=headers,
                          )
    assert response.status_code == 200
    assert response.json()['Status'] == True

# user/delete
def test_user_delete(login):
    api_client, user, token = login

    user_test = User.objects.filter(email=user.email).get()
    assert user_test.email == user.email

    url_view = 'user/delete/'
    url = URL_BASE + url_view
    headers = {'Authorization': f"Token {token}"}
    response = api_client.delete(url,
                          headers=headers,
                          )
    assert response.status_code == 200
    assert response.json()['Status'] == True

    try:
        user_test = User.objects.filter(email=user.email).get()
    except User.DoesNotExist as e:
        user_test = str(e)
    assert user_test == 'User matching query does not exist.'


# check /api/v1/user/details/
def test_user_details_get(login):
    api_client, user, token = login

    #test details_get
    url_view = 'user/details/'
    url = URL_BASE + url_view
    headers = {'Authorization': f"Token {token}", }
    response = api_client.get(url,
                              headers=headers,
                              )
    assert response.status_code == 200
    assert response.json()['id'] == 1
    assert response.json()['first_name'] == user.first_name
    assert response.json()['last_name'] == user.last_name
    assert response.json()['email'] == user.email


# test details_post
def test_user_details_post(login):
    api_client, user, token = login
    url_view = 'user/details/'
    url = URL_BASE + url_view
    #Меняем данные пользователя добавив "_new"
    password_new = f'{user.password}_new'
    first_name_new = f'{user.first_name}_new'
    last_name_new = f'{user.last_name}_new'
    data = {'first_name': first_name_new,
            'last_name': last_name_new,
            'password': password_new}
    headers = {'Authorization': f"Token {token}", }
    response = api_client.post(url,
                               headers=headers,
                               data=data,
                               )
    assert response.status_code == 200
    assert response.json()['Status'] == True

    # проверяем изменения

    # выходим из системы, чтобы проверить новый пароль
    url_logout = URL_BASE + 'user/logout/'
    response = api_client.post(url_logout, headers=headers,)
    assert response.status_code == 200
    assert response.json()['Status'] == True

    # входим в систему с новым паролем
    url_login = URL_BASE + 'user/login/'
    data = {'email': user.email,
            'password': password_new,
            }
    response = api_client.post(url_login,
                               data=data,
                               )
    token = response.json()['Token']
    assert response.status_code == 200
    assert response.json()['Status'] == True

    # проверяем новые данные пользователя
    headers = {'Authorization': f"Token {token}",}
    response = api_client.get(url, headers=headers,)
    assert response.json()['id'] == 1
    assert response.json()['first_name'] == first_name_new
    assert response.json()['last_name'] == last_name_new


# start tests
# >>> pytest
# tests coverage
# >>> pytest --cov=test_appstorespy_1
