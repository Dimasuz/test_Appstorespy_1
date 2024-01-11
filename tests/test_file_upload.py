import pytest
import warnings
from .conftest import URL_BASE

warnings.filterwarnings(action="ignore")

pytestmark = pytest.mark.django_db

@pytest.mark.parametrize("upload_file", ["txt", "exe"], indirect=True)
def test_upload(api_client, create_token, upload_file):
    """POST"""
    url_view = 'file/upload/'
    url = URL_BASE + url_view
    headers = {'Authorization': f"Token {create_token}",}
    with open(upload_file) as file:
        data = {"file": file,}
        response = api_client.post(url, headers=headers, data=data,)
    assert response.status_code == 201


@pytest.mark.parametrize("upload_file", ["txt"], indirect=True)
def test_upload(api_client, create_token, upload_file):
    """POST"""
    headers = {'Authorization': f"Token {create_token}",}
    # user logout
    url_view = 'user/logout/'
    url = URL_BASE + url_view
    response = api_client.get(url,
                          headers=headers,
                          )
    print(response)
    #
    url_view = 'file/upload/'
    url = URL_BASE + url_view
    with open(upload_file) as file:
        data = {"file": file,}
        response = api_client.post(url, headers=headers, data=data,)
    print(response)
    assert response.status_code == 201

