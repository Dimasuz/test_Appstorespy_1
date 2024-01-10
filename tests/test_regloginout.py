import pytest
import warnings

from rest_framework.authtoken.models import Token
# from regloginout.models import User

warnings.filterwarnings(action="ignore")

pytestmark = pytest.mark.django_db

URL_BASE = 'http://127.0.0.1:8000/api/v1/'

def test_example():
    assert True, "Just test example"


# check /api/v1/user/register
@pytest.mark.django_db
def test_user_register(register_user):
    api_client, user, conform_token, _ = register_user
    assert user
    assert conform_token


# check /api/v1/user/register/confirm
@pytest.mark.django_db
def test_register_confirm(register_user):
    api_client, user, conform_token, _ = register_user
    # user conformation
    url_view = 'user/register/confirm/'
    url = URL_BASE + url_view
    data = {'email': user.email,
            'token': conform_token,
            }
    response = api_client.post(url,
                           data=data,
                           )

    assert response.json()['Status'] == True
    assert response.status_code == 200


# check /api/v1/user/login
@pytest.mark.django_db
def test_login_logout(register_user):
    api_client, user, conform_token, password = register_user

    # user conformation
    url_view = 'user/register/confirm/'
    url = URL_BASE + url_view
    data = {'email': user.email,
            'token': conform_token,
            }
    response = api_client.post(url,
                               data=data,
                               )

    assert response.json()['Status'] == True
    assert response.status_code == 200

    # user login
    url_view = 'user/login/'
    url = URL_BASE + url_view
    print(user.email)
    print(user.password)
    data = {'email': user.email,
            'password': password,
            }
    response = api_client.post(url,
                           data=data,
                           )
    print(response)
    assert response.status_code == 200

    if response.status_code == 200:
        if response.json()['Status'] == False:
            token = None
        else:
            token = response.json()['Token']
    else:
        token = None
    assert token != None

    token_from_db, _ = Token.objects.get_or_create(user=user)
    assert token == token_from_db.key

    # user logout
    url_view = 'user/logout/'
    url = URL_BASE + url_view
    headers = {'Authorization': f"Token {token}"}
    response = api_client.get(url,
                          headers=headers,
                          )
    assert response.status_code == 200
    assert response.json()['Status'] == True


# # check /api/v1/user/login
# @pytest.mark.django_db
# def test_login(user_create):
#     api_client, user, password = user_create
#     print(User.objects.all())
#     # user login
#     url_view = 'user/login/'
#     url = URL_BASE + url_view
#     data = {'email': user.email,
#             'password': password,
#             }
#     print(data)
#     response = api_client.post(url,
#                            data=data,
#                            )
#     print(response.json())
#     assert response.status_code == 200
#     if response.status_code == 200:
#         if response.json()['Status'] == False:
#             token = None
#         else:
#             token = response.json()['Token']
#     else:
#         token = None
#     assert token != None


# start tests
# >>> pytest
# tests coverage
# >>> pytest --cov=test_appstorespy_1
