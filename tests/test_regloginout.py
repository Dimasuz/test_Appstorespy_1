import pytest
import warnings

warnings.filterwarnings(action="ignore")

pytestmark = pytest.mark.django_db

URL_BASE = 'http://127.0.0.1:8000/api/v1/'


def base_request(client, url_view='', method='get', token=None, data=None,):
    url = URL_BASE + url_view
    if token:
        headers = {'Authorization': f"Token {token}", }
    else:
        headers = None
    if method == 'get':
        response = client.get(url, headers=headers, data=data,)
    if method == 'post':
        response = client.post(url, headers=headers, data=data,)
    if method == 'put':
        response = client.put(url, headers=headers, data=data,)
    if method == 'delete':
        response = client.delete(url, headers=headers, data=data,)
    try:
        response.json()
    except BaseException:
        print('Ошибка json')
    else:
        return response.status_code, response.json()

def test_example():
    assert True, "Just test example"

# check /api/v1/user/register
def test_user_register(client, register_user):
    user = register_user
    assert user['status_code'] == 200
    assert user['status'] == True
    # assert user['task_id']


# check /api/v1/user/register/confirm
def test_register_confirm(client, register_user):
    user = register_user
    # user conformation
    url_view = 'user/register/confirm/'
    url = URL_BASE + url_view
    data = {'email': user['email'],
            'token': user['conform_token'],
            }
    response = client.post(url,
                           data=data,
                           )

    assert response.json()['Status'] == True
    assert response.status_code == 200


# check /api/v1/user/login
def test_login(client,register_user):
    user = register_user
    # user conformation for login
    url_view = 'user/register/confirm/'
    url = URL_BASE + url_view
    data = {'email': user['email'],
            'token': user['conform_token'],
            }
    client.post(url, data=data,)
    # user login
    url_view = 'user/login/'
    url = URL_BASE + url_view
    data = {'email': user['email'],
            'password': user['password'],
            }
    response = client.post(url,
                           data=data,
                           )
    assert response.status_code == 200
    if response.status_code == 200:
        if response.json()['Status'] == False:
            token = None
        else:
            token = response.json()['Token']
    else:
        token = None
    assert token != None


def test_logout(client, user_create_login):
    user, token = user_create_login
    # user logout
    url_view = 'user/logout/'
    url = URL_BASE + url_view
    headers = {'Authorization': token}
    response = client.get(url,
                           headers=headers,
                           )
    assert response.status_code == 200
    assert response.json()['Status'] == True


# start tests
# >>> pytest
# tests coverage
# >>> pytest --cov=test_appstorespy_1