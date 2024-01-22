import time
import uuid
import requests
from pprint import pprint

url_base = 'http://0.0.0.0:8000/api/v1/'
# url_base = 'http://127.0.0.1:8000/api/v1/'
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
def user_register(email=None, password=None):
    url_view = 'user/register/'
    if not email:
        email = int(input('Введите email: '))
    if not password:
        password = int(input('Введите пароль: '))
    data ={'first_name': f'first_name_{email}',
          'last_name': f'last_name_{email}',
          'email': email,
          'password': f'Password_{email}',
          }
    response, json_status = base_request(url_view=url_view, method='post', data=data)
    if json_status:
        # token_confirm = response.json()['token']['token']
        task_id = response.json()['task_id']
    else:
        task_id = None
    print(f'Token confirm: {task_id}')
    return task_id


# confirm email----------------------
def confirm():
    url_view = 'user/register/confirm/'
    email = input('Введите email пользователя: ')
    token = input('Введите token: ')
    data= {'email': email,
           'token': token,
           }
    response, json_status = base_request(url_view=url_view, method='post', data=data)


# login user -----------------------
def login(email=None, password=None):
    url_view = 'user/login/'
    if not email:
        email = int(input('Введите email пользователя = '))
    if not password:
        password = f'Password_{email}'
    data= {'email': email,
           'password': password,
           }
    response, json_status = base_request(url_view=url_view, method='post', data=data)
    if response.status_code == 200 and json_status:
        if response.json()['Status'] == False:
            token_login = None
        else:
            token_login = response.json()['Token']
    else:
        token_login = None
    return token_login

# user/details/ -----------------------------
def details_get(token=None):
    url_view = 'user/details/'
    if not token:
        token = input('Введите token пользователя = ')
    headers = get_headers(token=token)
    response, json_status = base_request(url_view=url_view, method='get', headers=headers,)
    return response

def details_post(token=None, **kwargs):
    url_view = 'user/details/'
    if not token:
        token = input('Введите token пользователя = ')
    headers = get_headers(token=token)
    response, json_status = base_request(url_view=url_view, method='post', data=kwargs, headers=headers)
    return response

# logout user-----------------------
def logout(token=None):
    url_view = 'user/logout/'
    if not token:
        token = input('Введите token пользователя = ')
    headers = get_headers(token=token)
    response, json_status = base_request(url_view=url_view, method='get', headers=headers,)


# celery tesk status-----------------------
def celery_status(task_id=None):
    url_view = 'user/celery_status'
    if not task_id:
        task_id = input('Введите task_id = ')
    if task_id:
            celery_status = "PENDING"
            while celery_status == "PENDING":
                # status = requests.get(f"{url_base}{url_view}?task_id={task_id}").json()["status"]
                response, json_status = base_request(url_view=url_view, method='get', params={'task_id': task_id})
                celery_status = response.json()['celery_status']
                print(f'{celery_status=}')
                # time.sleep(1)
                if celery_status == "PENDING":
                    if input('Stop? y/n') == 'y':
                        return
                    else:
                        celery_status = "PENDING"

def api_test():
    a = None
    a = input('Регистрация - 1, Подтверждение почты - 2, Логин - 3, Логаут - 4, \n Детали пользователя (получить) - 5, Детали пользователя (изменить) - 6, или запрос таски - 7 : ')

    if a == '1':
        email = input('Введите {адрес} @mail.ru: ')
        email = email + '@mail.ru'
        # num = time.time()
        # num = str(uuid.uuid4())
        password = f'Password_{email}'
        task_id = user_register(email=email, password=password)
        celery = input('Запросить очередь celery? ')
        if celery:
            celery_status(task_id)
        else:
            return
    elif a == '2':
        confirm()
    elif a == '3':
        email = input('Введите {адрес} @mail.ru: ')
        email = email + '@mail.ru'
        if input('Стандартный пароль? Y '):
            login(email=email)
        else:
            password = input('Введите пароль: ')
            login(email=email, password=password)
    elif a == '4':
        logout()
    elif a == '5':
        email = input('Введите {адрес} @mail.ru: ')
        email = email + '@mail.ru'
        token = login(email=email)
        details_get(token)
    elif a == '6':
        email = input('Введите {адрес} @mail.ru: ')
        email = email + '@mail.ru'
        print('Входим в систему.')
        token = login(email=email)
        print('Меняем данные пользователя добавив "_new".')
        password_new = f'Password_{email}_new'
        # password_new = 'new'
        data = {'first_name': f'first_name_{email}_new',
                'last_name': f'last_name_6021185@mail.ru{email}_new',
                'password': password_new}
        details_post(token, **data)
        details_get(token)
        print('Выходим из системы')
        logout()
        if input('Меняем данные пользователя обратно? Y '):
            print('Входим в систему.')
            token = login(email=email, password=password_new)
            data = {'first_name': f'first_name_{email}',
                    'last_name': f'last_name_{email}',
                    'password': f'Password_{email}'}
            details_post(token, **data)
            details_get(token)
            print('Выходим из системы')
            logout(token)
    elif a == '7':
        celery_status()
    else:
        pass
    return None

if __name__ == "__main__":
    api_test()

    # curl --location --request POST 'http://localhost:8000/api/upload-file/' \
    # --form 'file=@"/path/to/yourfile.pdf"'