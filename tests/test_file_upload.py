import os
import warnings

import pytest
from django.conf import settings

from uploader.models import UploadFile, FileOnDisk, FileInDb

from .conftest import URL_BASE

warnings.filterwarnings(action="ignore")

pytestmark = pytest.mark.django_db


url = ['disk', 'db']
url_file = url[1]

# file/upload/

# @pytest.mark.parametrize("tmp_file", ["txt", "exe"], indirect=True)
@pytest.mark.parametrize("tmp_file", ["txt"], indirect=True)
def test_upload(login, tmp_file):
    """POST"""
    url_view = f'file/{url_file}/upload/'
    url = URL_BASE + url_view
    api_client, user, token = login
    headers = {'Authorization': f"Token {token}",}
    with open(tmp_file, 'rb') as file:
        data = {"file": file,}
        response = api_client.post(url, headers=headers, data=data,)

    file_id = response.json()['File_id']

    if url_file == 'db':
        uploaded_file = FileInDb.objects.all().filter(pk=file_id)[0].file
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.file.name)
    elif url_file == 'disk':
        uploaded_file = FileOnDisk.objects.all().filter(pk=file_id)[0].file
        file_path = uploaded_file

    assert response.status_code == 201
    assert response.json()['Status'] == True
    assert type(response.json()['File_id']) == int
    assert uploaded_file
    # assert response.json()['Task_id']

    # clear disk
    os.remove(file_path)


@pytest.mark.parametrize("tmp_file", ["txt"], indirect=True)
def test_upload_not_authorization(login, tmp_file):
    api_client, user, token = login
    url_view = 'user/logout/'
    url = URL_BASE + url_view
    headers = {'Authorization': f"Token {token}"}
    api_client.post(url, headers=headers,)

    """POST"""
    url_view = f'file/{url_file}/upload/'
    url = URL_BASE + url_view
    with open(tmp_file) as file:
        data = {"file": file,}
        response = api_client.post(url, headers=headers, data=data,)

    assert response.status_code == 401


# file/download/

@pytest.mark.parametrize("tmp_file", ["txt"], indirect=True)
def test_download(login, tmp_file):
    # prepare file by POST
    url_view = f'file/{url_file}/upload/'
    url = URL_BASE + url_view
    api_client, user, token = login
    headers = {'Authorization': f"Token {token}",}
    with open(tmp_file, 'rb') as file_upload:
        data_post = {"file": file_upload,}
        response = api_client.post(url, headers=headers, data=data_post,)
        print(response.json())
        file_id = response.json()['File_id']
        file_upload.seek(0)

        """GET"""
        url_view = f'file/{url_file}/download/'
        url = URL_BASE + url_view
        data_get = {'file_id': file_id,}
        response = api_client.get(url, headers=headers, data=data_get,)

        assert response.status_code == 200
        assert file_upload.read() == response.getvalue()

    # clear disk
    if url_file == 'db':
        uploaded_file = FileInDb.objects.all().filter(pk=file_id)[0].file
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.file.name)
    elif url_file == 'disk':
        file_path = FileOnDisk.objects.all().filter(pk=file_id)[0].file

    os.remove(file_path)


#------------------------------------------------------------------------
# @pytest.mark.parametrize("tmp_file", ["txt"], indirect=True)
# def test_download_wrong_user(login, tmp_file, create_token):
#     # prepare file
#     url_view = f'file/{url_file}/upload/'
#     url = URL_BASE + url_view
#     api_client, user, token = login
#     headers = {'Authorization': f"Token {token}", }
#     file_tmp_path = tmp_file
#     with open(file_tmp_path, 'rb') as file_upload:
#         data = {"file": file_upload, }
#         response = api_client.post(url, headers=headers, data=data, )
#     file_id = response.json()['File_id']
#     file_uploaded = UploadFile.objects.all().filter(pk=file_id)[0]
#     file_uploaded_path = os.path.join(settings.FILES_UPLOADED, file_uploaded.file)
#
#     """GET"""
#     url_view = f'file/{url_file}/download/'
#     url = URL_BASE + url_view
#     token_wrong_user = create_token
#     headers = {'Authorization': f"Token {token_wrong_user}", }
#     data = {'file_id': file_id, }
#     response = api_client.get(url, headers=headers, data=data, )
#
#     assert response.status_code == 403
#     assert not response.json()['Status']
#     assert response.json()['Error'] == 'You try to get not yours file.'
#
#     # clear
#     os.remove(file_uploaded_path)

#     # print(response.json())
#     # assert False






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
