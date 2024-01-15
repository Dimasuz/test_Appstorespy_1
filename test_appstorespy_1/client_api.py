import time
import requests
from pprint import pprint

url_base = 'http://0.0.0.0:8000/api/v1/'
# url_base = 'http://0.0.0.0:8000/api/v1/auth0/'

def base_request(url_view='', method='get', headers=None, data=None, params=None):
    url = url_base + url_view
    print()
    print(method, url_view)
    if method == 'get':
        response = requests.get(url, headers=headers, params=params)
    if method == 'post':
        response = requests.post(url, headers=headers, data=data,)
    if method == 'put':
        response = requests.put(url, headers=headers, data=data,)
    if method == 'delete':
        response = requests.delete(url, headers=headers, data=data,)
    print(response.status_code)
    try:
        response.json()
    except BaseException as e:
        print('JSON ERROR:')
        pprint(e)
        return response, None
    else:
        print('JSON:')
        pprint(response.json())
        return response, True

def get_headers(token=None, content_type=None):
    authorization = f"Token {token}"
    if content_type:
        headers = {'Content-Type': content_type, 'Authorization': authorization,}
    else:
        headers = {'Authorization': authorization,}
    return headers

# registration-----------
def user_register(num=None):
    url_view = 'user/register/'
    if not num:
        num = int(input('Введите номер пользователя: '))

    data ={'first_name': f'first_name_{num}',
          'last_name': f'last_name_{num}',
          'email': f'email_{num}@mail.ru',
          'password': f'Password_{num}',
          }
    response, json_status = base_request(url_view=url_view, method='post', data=data)
    if json_status:
        token_confirm = response.json()['token']['token']
    else:
        token_confirm = None
    print(f'Token confirm: {token_confirm}')
    return token_confirm, num


# confirm email----------------------
def confirm(token=None, num=None):
    url_view = 'user/register/confirm/'
    if not num:
        num = input('Введите номер пользователя: ')
    if not token:
        token = input('Введите token: ')


    data= {'email': f'email_{num}@mail.ru',
           'token': token,
           }
    response, json_status = base_request(url_view=url_view, method='post', data=data)

    if response.status_code == 200 and json_status:
        if response.json()['Status'] == False:
            print('Нет такого пользователя')
        else:
            print('User confirm succesful.')


# login user -----------------------
def login(num=None):
    url_view = 'user/login/'
    if not num:
        num = int(input('Введите номер пользователя (или 0) = '))
    if num == 0:
        email = input('Введите email пользователя = ')
        num = input('Введите номер пароля = ')
    else:
        email = f'email_{num}@mail.ru'
    password = f'Password_{num}'
    data= {'email': email,
           'password': password,
           }
    response, json_status = base_request(url_view=url_view, method='post', data=data)
    if response.status_code == 200 and json_status:
        if response.json()['Status'] == False:
            print('Нет такого пользователя')
            token_login = None
        else:
            token_login = response.json()['Token']
            print(f'Token login: {token_login}')
    else:
        token_login = None
    return token_login


# logout user-----------------------
def logout(token=None):
    url_view = 'user/logout/'
    if not token:
        token = input('Введите token пользователя = ')
    headers = get_headers(token=token)
    response, json_status = base_request(url_view=url_view, method='get', headers=headers,)
    if response.status_code == 200 and json_status:
        if response.json()['Status'] == False:
            print('Нет такого пользователя')
        else:
            print('Logout successful.')


def api_test():
    a = None

    a = input('Регистрация - 1, Подтверждение почты - 2, Логин - 3, Логаут - 4, или все сразу - 0 : ')
    if a == '0':
        num = time.time()
        token, _ = user_register(num)
        confirm(token, num)
        token = login(num)
        logout(token)
    elif a == '1':
        user_register()
    elif a == '2':
        confirm()
    elif a == '3':
        login()
    elif a == 4 :
        logout()
    else:
        pass
    return None

if __name__ == "__main__":
    api_test()

    # curl --location --request POST 'http://localhost:8000/api/upload-file/' \
    # --form 'file=@"/path/to/yourfile.pdf"'