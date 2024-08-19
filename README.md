# Проект

## Установка
Стабильно работает на Python 3.12
1. Создаём venv
```
python -m venv venv
```
2. Активируем (Linux) виртуальное окружение
```
. venv/bin/activate
```
3. Устанавливаем зависимости
```
pip install -r requirements.txt
```
4. Далее необходимо настроить бд. Предполагается использование PostgreSQL или MySQL. Для этого необходимо в файле
`askme/settings.py` указать настройки по аналогии:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'askme',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}
```   
5. После того, как БД настроена можно использовать команду, для наполнения базы тестовыми данными
```
python manage.py fill_db <ratio>
```
ratio - количество пользователей
6. Далее настраивается nginx. Для Debian. Помещаем файл `nginx.conf` в директорию `/etc/nginx/`, предварительно сохранив
бекап имеющегося там файла `nginx.conf`:
```nginx
user  misha; # Указываем своего юзера, от которого запускается nginx

worker_processes  1;

events {
    worker_connections  1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;

    access_log  /var/log/nginx/access.log;
    error_log   /var/log/nginx/error.log;

    sendfile        on;
    keepalive_timeout  65;

    include /etc/nginx/sites-enabled/askme.conf;
}
```
Кроме того, нужно поместить файл `askme.conf` в `/etc/nginx/sites-enabled/askme.conf`, предварительно указав свой путь
к проекту:
```nginx
upstream askme {
    server localhost:8081;
}

server {
    listen 80 default_server;
    server_name askme.com;
	    
    location /static/ {
    	# Path to project directory
    	root /home/misha/Techpark-1-WEB;
    }
    
    location /uploads/ {
    	# Path to project directory
    	root /home/misha/Techpark-1-WEB;
    }

    location / {
        proxy_pass http://askme;
        proxy_set_header Host $host;
    }
}
```
7. После настройки конфигурации nginx, требуется проверить конфигурацию:
```
sudo nginx -t
```
Если всё ОК, то перезапускаем nginx:
```
sudo systemctl restart nginx
```
8. Из директории проекта запустить gunicorn:
```
gunicorn askme.wsgi
```
**P.S. Проект можно запустить, пропустив шаги 6 – 8, а также в шаге 4 обойтись без установки сторонних БД.**  
Для этого в шаге 4 можно  настроить встроенный в Python SQLite, далее заполнив БД как в шаге 5. И запустить отладочный
сервер Django, который используется только для разработки, но также может использоваться для знакомства с основным функционалом.
```
python manage.py runserver <IP-address:port>
```
`<IP-address:port>` - IP-адрес и порт, например `192.168.3.10:80`. **Не обязателен**. По умолчанию `127.0.0.1:8000`

## Баги

1. Форма настроек пользовавателя. Не допускается сохранение текущих настроек, при смене одной из них. Например, при изменении имени, необходимо обязательно сменить и e-mail.
   (blank = True?)
2. Добавленный вопрос с нулевым количеством лайков во вкладке Hot отображается выше, чем другие посты с большим рейтингом
## Идеи
1. ~~При нажатии лайка или дизлайка должно отображаться нажат лайк или нет. Перезагрзка страницы не должна менять статуса~~
