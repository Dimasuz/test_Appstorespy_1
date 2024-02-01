import os
import uuid

import pytest
from model_bakery import baker
from rest_framework.authtoken.models import Token

from regloginout.models import ConfirmEmailToken, User

# from django.contrib.auth import authenticate, login, logout


URL_BASE = "http://127.0.0.1:8000/api/v1/"


# фикстура для api-client
@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


# фикстура для регистрации и получения ConfirmEmailToken
@pytest.fixture
def register_user(api_client):
    url_view = "user/register/"
    url = URL_BASE + url_view
    num = str(uuid.uuid4())
    email = f"email_{num}@mail.ru"
    password = f"Password_{num}"
    data = {
        "first_name": f"first_name_{num}",
        "last_name": f"last_name_{num}",
        "email": email,
        "password": password,
    }
    response = api_client.post(
        url,
        data=data,
    )
    user = User.objects.all().filter(email=email).get()
    conform_token = (
        ConfirmEmailToken.objects.filter(user_id=user.id)
        .values_list("key", flat=True)
        .get()
    )
    return api_client, user, conform_token, password, response


@pytest.fixture
def register_confirm(register_user):
    api_client, user, confirm_token, password, _ = register_user
    # user confirmation
    url_view = "user/register/confirm/"
    url = URL_BASE + url_view
    data = {
        "email": user.email,
        "token": confirm_token,
    }
    response = api_client.post(
        url,
        data=data,
    )
    return api_client, user, password, response


@pytest.fixture
def login(register_confirm):
    api_client, user, password, _ = register_confirm
    url_view = "user/login/"
    url = URL_BASE + url_view
    data = {
        "email": user.email,
        "password": password,
    }
    response = api_client.post(
        url,
        data=data,
    )
    token = response.json()["Token"]
    return api_client, user, token


@pytest.fixture()
def create_token():
    user = baker.make(
        User,
        is_active=True,
    )
    token, _ = Token.objects.get_or_create(user=user)
    return token.key


@pytest.fixture
def tmp_file(tmp_path, request):
    file_name = "test_file_" + str(uuid.uuid4())
    file_ext = request.param
    file_name = os.path.join(tmp_path, f"{file_name}.{file_ext}")
    with open(file_name, "w+") as file:
        # file.write(io.BytesIO(b"some initial text data"))
        file.write(f"test {file_name}")
    return file_name


# for auth0
# https://github.com/mozilla-iam/auth0-tests/tree/master
