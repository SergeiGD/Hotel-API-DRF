## Инструкция по запуску:
1. Находясь в папке с проектом создайте .env файл со следующим содержанием:
```bash
DB_NAME=ваше имя базы данных
DB_USER=ваш логин к базе данных
DB_PASSWORD=ваш пароль к базе данных
DB_PORT=ваш порт для базы данных (должен быть свободен)
KEY=ваш секретный ключ джанго
EMAIL_USER=почта, с которой будут отправляться письма (регистрация, сбос пароля...)
EMAIL_PASSWORD=пароль от почты, с которой будут отправляться письма
EMAIL_HOST=хостинг почты (по умолчанию smtp.gmail.com)
```
Пример:
```bash
DB_NAME=hotel_db
DB_USER=user
DB_PASSWORD=passwd
DB_PORT=5454
KEY=@@)*r3&2f0=%t^@bnom9@916(z=3-2e_iqqr90(r_v@foum(q^
EMAIL_USER=hotel_email@gmai.com
EMAIL_PASSWORD=sdfzfgrtq
```
2) Соберите и запустите контейнеры:
```
docker-compose up --build
```