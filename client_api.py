import os.path
import time
import uuid
from pprint import pprint

import requests

url_base = "http://0.0.0.0:8000/api/v1/"
# url_base = 'http://127.0.0.1:8000/api/v1/'
# url_base = 'http://0.0.0.0:8000/api/v1/auth0/'


def base_request(
    url_view="", method="get", headers=None, data=None, params=None, files=None
):
    url = url_base + url_view
    print()
    print(method, url_view)
    if method == "get":
        response = requests.get(url, headers=headers, params=params, timeout=5, verify=False)
    if method == "post":
        response = requests.post(url, headers=headers, data=data, files=files)
    if method == "put":
        response = requests.put(
            url,
            headers=headers,
            data=data,
        )
    if method == "delete":
        response = requests.delete(
            url,
            headers=headers,
            data=data,
        )
    print(response.status_code)
    try:
        response.json()
    except BaseException as e:
        print("JSON ERROR:")
        pprint(e)
        return response, None
    else:
        print("JSON:")
        pprint(response.json())
        return response, True


def get_headers(token=None, content_type=None):
    authorization = f"Token {token}"
    if content_type:
        headers = {
            "Content-Type": content_type,
            "Authorization": authorization,
        }
    else:
        headers = {
            "Authorization": authorization,
        }
    return headers


# registration-----------
def user_register(email=None, password=None):
    url_view = "user/register/"
    if not email:
        email = int(input("Введите email: "))
    if not password:
        password = int(input("Введите пароль: "))
    data = {
        "first_name": f"first_name_{email}",
        "last_name": f"last_name_{email}",
        "email": email,
        "password": f"Password_{email}",
    }
    response, json_status = base_request(url_view=url_view, method="post", data=data)
    if response.status_code == 200 and json_status:
        if response.json()["Status"] == False:
            task_id = None
            token_confirm = None
        else:
            task_id = response.json()["task_id"]
            token_confirm = response.json()["token"]
    else:
        task_id = None
        token_confirm = None
    return task_id, token_confirm


# confirm email----------------------
def confirm(email=None, token=None):
    url_view = "user/register/confirm/"
    if not email:
        email = input("Введите email пользователя: ")
    if not token:
        token = input("Введите token: ")
    data = {
        "email": email,
        "token": token,
    }
    response, json_status = base_request(url_view=url_view, method="post", data=data)
    return response


# login user -----------------------
def login(email=None, password=None):
    url_view = "user/login/"
    if not email:
        email = input("Введите email пользователя = ")
    if not password:
        password = f"Password_{email}"
    data = {
        "email": email,
        "password": password,
    }
    response, json_status = base_request(url_view=url_view, method="post", data=data)
    if response.status_code == 200 and json_status:
        if response.json()["Status"] == False:
            token_login = None
        else:
            token_login = response.json()["Token"]
    else:
        token_login = None
    return token_login


# user/details/ -----------------------------
def details_get(token=None):
    url_view = "user/details/"
    if not token:
        token = input("Введите token пользователя = ")
    headers = get_headers(token=token)
    response, json_status = base_request(
        url_view=url_view,
        method="get",
        headers=headers,
    )
    return response


def details_post(token=None, **kwargs):
    url_view = "user/details/"
    if not token:
        token = input("Введите token пользователя = ")
    headers = get_headers(token=token)
    response, json_status = base_request(
        url_view=url_view, method="post", data=kwargs, headers=headers
    )
    return response


# logout user-----------------------
def logout(token=None):
    url_view = "user/logout/"
    if not token:
        token = input("Введите token пользователя = ")
    headers = get_headers(token=token)
    response, json_status = base_request(
        url_view=url_view,
        method="post",
        headers=headers,
    )
    return response


# logout user-----------------------
def delete(token=None):
    url_view = "user/delete/"
    if not token:
        token = input("Введите token пользователя = ")
    headers = get_headers(token=token)
    response, json_status = base_request(
        url_view=url_view,
        method="delete",
        headers=headers,
    )
    return response


# file/upload/
def upload(token=None):
    url_view = "file/db/upload/"
    if not token:
        token = input("Введите token пользователя = ")
    headers = get_headers(token=token)

    CURR_DIR = os.path.dirname(os.path.realpath(__file__))
    file = os.path.join(CURR_DIR, "test_file.txt")

    uploaded_file_name = "test_uploaded_file.txt"
    with open(file, "r+") as f:
        f.write(f'begin - {str(time.time())} - end')
        f.seek(0)
        files = {"file": (uploaded_file_name, f, "text/x-spam")}
        try:
            response, json_status = base_request(
                url_view=url_view, method="post", headers=headers, files=files
            )
            return response
        except Exception as e:
            return e

    # url = url_base + url_view
    # files = {'file': (uploaded_file_name, open(file, 'rb'), 'text/x-spam')}
    # try:
    #     response = requests.post(url, headers=headers, files=files)
    #     return response
    # except Exception as e:
    #     return e


# file/upload/
def download(token=None, file_id=None):
    url_view = "file/db/download/"
    if not token:
        token = input("Введите token пользователя = ")
    if not file_id:
        file_id = int(input("Введите file_id = "))
    headers = get_headers(token=token)
    params = {
        "file_id": file_id,
    }
    # response = requests.get(url_base + url_view, headers=headers, params=params)
    response, json_status = base_request(
        url_view=url_view,
        method="get",
        headers=headers,
        params=params,
    )
    # print(response.json())
    print(type(response))
    print(response.text)
    print(response.content)
    if response.status_code == 200:
        with open('file_test_download.txt', 'w') as f:
            f.write(response.text)
    else:
        return response


# file/processing/
def processing(token=None, file_id=None):
    url_view = "file/processing/"
    if not token:
        token = input("Введите token пользователя = ")
    if not file_id:
        file_id = input("Введите file_id = ")
    headers = get_headers(token=token)
    params = {
        "file_id": file_id,
    }
    response, json_status = base_request(
        url_view=url_view,
        method="get",
        headers=headers,
        params=params,
    )

    return response


# celery tesk status-----------------------
def celery_status(task_id=None):
    url_view = "celery_status/"
    if not task_id:
        task_id = input("Введите task_id = ")
    if task_id:
        celery_status = "-"
        while not celery_status == "SUCCESS":
            # status = requests.get(f"{url_base}{url_view}?task_id={task_id}").json()["status"]
            response, json_status = base_request(
                url_view=url_view, method="get", params={"task_id": task_id}
            )
            celery_status = response.json()["Status"]
            file = response.json()["Result"]
            time.sleep(1)
            if not celery_status == "SUCCESS":
                if input("Stop? y/n") == "y":
                    return celery_status
        return celery_status, file


# /user/password_reset/ ----------------------------
def password_reset(email=None):
    url_view = "user/password_reset/"
    if not email:
        email = input("Введите email пользователя = ")
    data = {
        "email": email,
    }
    response, json_status = base_request(url_view=url_view, method="post", data=data)


# /user/password_reset/confirm/ ----------------------------
def password_reset_confirm(token=None, password=None):
    url_view = "user/password_reset/confirm/"
    if not token:
        token = input("Введите token = ")
    if not password:
        password = input("Введите password = ")
    data = {
        "token": token,
        "password": password,
    }
    response, json_status = base_request(url_view=url_view, method="post", data=data)


def api_test():
    a = None
    a = input(
        "Регистрация - 1, Подтверждение почты - 2, Логин - 3\
    , Логаут - 4, Удалить пользователя - 5 \n Смена пароля - 11\ "
        "\nДетали пользователя (получить) - 6, Детали пользователя (изменить) - 7, \nзагрузка файла - 22, загрузка файла с id - 21 или запрос таски - 8 : "
    )
    # регистраиця нового пользователя
    if a == "0":
        # num = time.time()
        # email = str(uuid.uuid4())
        email = input("Введите {адрес} @mail.ru: ")
        email = email + "@mail.ru"
        password = f"Password_{email}"
        _, token = user_register(email=email, password=password)
        confirm(email=email, token=token)
        token = login(email=email)
        logout(token)
        token = login(email=email)
        delete(token)

    elif a == "1":
        email = input("Введите {адрес} @mail.ru: ")
        email = email + "@mail.ru"
        password = f"Password_{email}"
        response = user_register(email=email, password=password)
        celery = input("Запросить очередь celery? ")
        if celery:
            celery_status(response["task_id"])
        else:
            return
    # подтверждение почты нового пользователя
    elif a == "2":
        email = input("Введите {адрес} @mail.ru: ")
        email = email + "@mail.ru"
        confirm(email=email)
    # вход в систему
    elif a == "3":
        email = input("Введите {адрес} @mail.ru: ")
        email = email + "@mail.ru"
        if input("Стандартный пароль? Y "):
            login(email=email)
        else:
            password = input("Введите пароль: ")
            login(email=email, password=password)
    # выход из системы
    elif a == "4":
        logout()
    # удаление пользователя
    elif a == "5":
        delete()

    # запрос данных пользователя
    elif a == "6":
        email = input("Введите {адрес} @mail.ru: ")
        email = email + "@mail.ru"
        token = login(email=email)
        details_get(token)
    # изменение данных пользователя
    elif a == "7":
        email = input("Введите {адрес} @mail.ru: ")
        email = email + "@mail.ru"
        print("Входим в систему.")
        token = login(email=email)
        print('Меняем данные пользователя добавив "_new".')
        password_new = f"Password_{email}_new"
        # password_new = 'new'
        data = {
            "first_name": f"first_name_{email}_new",
            "last_name": f"last_name_6021185@mail.ru{email}_new",
            "password": password_new,
        }
        details_post(token, **data)
        details_get(token)
        print("Выходим из системы")
        logout()
        if input("Меняем данные пользователя обратно? Y "):
            print("Входим в систему.")
            token = login(email=email, password=password_new)
            data = {
                "first_name": f"first_name_{email}",
                "last_name": f"last_name_{email}",
                "password": f"Password_{email}",
            }
            details_post(token, **data)
            details_get(token)
            print("Выходим из системы")
            logout(token)
    # запрос таски
    elif a == "8":
        celery_status()
    elif a == "11":
        password_reset()
        password_reset_confirm()
    elif a == "22":
        email = input("Введите {адрес} @mail.ru: ")
        email = email + "@mail.ru"
        password = f"Password_{email}"
        _, token = user_register(email=email, password=password)
        confirm(email=email, token=token)
        token = login(email=email)
        print(f"{token=}")
        print("Загрузка файла.")
        input("Do?")
        file_id = upload(token=token).json()["File_id"]
        print(f"{file_id=}")
        print(f"Обработка файла с id - {file_id}.")
        input("Do?")
        task_id = processing(token=token, file_id=file_id)
        print(task_id.json())
        task_id = task_id.json()["Task_id"]
        print(f"Запрос таски - {task_id}.")
        input("Do?")
        print(celery_status(task_id=task_id))
        print(f"Скачивание файла с id - {file_id}.")
        input("Do?")
        download(token=token, file_id=file_id)
        print(f"Удаление из базы пользователя.")
        input("Do?")
        delete(token=token)
    elif a == "21":
        token = '21855aebd65f2a69e457874415ca4b1a620540aa'
        upload(token=token)
    elif a == "20":
        token = '21855aebd65f2a69e457874415ca4b1a620540aa'
        download(token=token)

    else:
        pass
    return None


if __name__ == "__main__":
    api_test()

    # curl --location --request POST 'http://localhost:8000/api/upload-file/' \
    # --form 'file=@"/path/to/yourfile.pdf"'


