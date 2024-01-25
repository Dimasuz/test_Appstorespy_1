import pytest
import warnings
from .conftest import URL_BASE

warnings.filterwarnings(action="ignore")

pytestmark = pytest.mark.django_db

@pytest.mark.parametrize("tmp_file", ["txt", "exe"], indirect=True)
def test_upload(api_client, create_token, tmp_file):
    """POST"""
    url_view = 'file/upload/'
    url = URL_BASE + url_view
    headers = {'Authorization': f"Token {create_token}",}
    with open(tmp_file) as file:
        data = {"file": file,}
        response = api_client.post(url, headers=headers, data=data,)

    assert response.status_code == 201


@pytest.mark.parametrize("tmp_file", ["txt"], indirect=True)
def test_upload_not_authorization(login, tmp_file):
    api_client, user, token = login
    url_view = 'user/logout/'
    url = URL_BASE + url_view
    headers = {'Authorization': f"Token {token}"}
    api_client.post(url, headers=headers,)

    """POST"""
    url_view = 'file/upload/'
    url = URL_BASE + url_view
    with open(tmp_file) as file:
        data = {"file": file,}
        response = api_client.post(url, headers=headers, data=data,)

    assert response.status_code == 401

# pytest --ignore=tests/test_regloginout.py
