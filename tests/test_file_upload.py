import os
import warnings

import pytest

from uploader.models import UploadFile

from .conftest import URL_BASE

warnings.filterwarnings(action="ignore")

pytestmark = pytest.mark.django_db


# file/upload/
# @pytest.mark.parametrize("tmp_file", ["txt", "exe"], indirect=True)
@pytest.mark.parametrize("tmp_file", ["txt"], indirect=True)
def test_upload(api_client, create_token, tmp_file):
    """POST"""
    url_view = 'file/upload/'
    url = URL_BASE + url_view
    headers = {'Authorization': f"Token {create_token}",}
    with open(tmp_file) as file:
        data = {"file": file,}
        response = api_client.post(url, headers=headers, data=data,)

    file_id = response.json()['File_id']
    file = UploadFile.objects.all().filter(pk=file_id)[0]
    os.remove(os.path.join(file.file_path, file.file))

    assert response.status_code == 201
    assert response.json()['Status'] == True
    assert type(response.json()['File_id']) == int
    # assert response.json()['Task_id']


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


# file/download/
@pytest.mark.parametrize("tmp_file", ["txt"], indirect=True)
def test_download(api_client, create_token, tmp_file):
    # prepare file
    url_view = 'file/upload/'
    url = URL_BASE + url_view
    headers = {'Authorization': f"Token {create_token}",}
    file_tmp_path = tmp_file
    with open(file_tmp_path, 'rb') as file_upload:
        data = {"file": file_upload,}
        response = api_client.post(url, headers=headers, data=data,)
    file_id = response.json()['File_id']
    file_uploaded = UploadFile.objects.all().filter(pk=file_id)[0]
    file_uploaded_path = os.path.join(file_uploaded.file_path, file_uploaded.file)

    """GET"""
    url_view = 'file/download/'
    url = URL_BASE + url_view
    data = {'file_id': file_id,}
    response = api_client.get(url, headers=headers, data=data,)

    assert response.status_code == 200

    with open(file_uploaded_path, 'rb') as f:
        assert f.read() == response.getvalue()

    # clear
    os.remove(file_uploaded_path)


# # запрос статуса Селери в pytest почему-то возвращает None
# # хотя через Postman все работает даже с таской из pytest
# # celery_status/
# @pytest.mark.parametrize("tmp_file", ["txt"], indirect=True)
# def test_celery_status(api_client, create_token, tmp_file):
#     # preparation test file
#     url_view = 'file/upload/'
#     url = URL_BASE + url_view
#     headers = {'Authorization': f"Token {create_token}", }
#     with open(tmp_file) as file:
#         data = {"file": file, }
#         response = api_client.post(url, headers=headers, data=data,)
#     task_id = response.json()['Task_id']
#     print(task_id)
#     file = response.json()['File']
#     print(file)
#     # check celery_status/
#     url_view = 'celery_status/'
#     url = URL_BASE + url_view
#     celery_status = "PENDING"
#     while celery_status == "PENDING":
#         response = api_client.get(url, params={'task_id': task_id})
#         # здесь выдает ошибку:
#         # "AssertionError: Expected a `Response`, `HttpResponse` or `HttpStreamingResponse`
#         # to be returned from the view, but received a `<class 'NoneType'"
#         # и запрос статуса Селери в pytest почему-то возвращает None,
#         # хотя через Postman все работает даже с таской из pytest
#         celery_status = response.json()['Status']
#         time.sleep(1)
#     os.remove(file)
#     assert celery_status in ['PENDING', 'STARTED', 'SUCCESS']
#     assert response.status_code == 201


# pytest --ignore=tests/test_regloginout.py
