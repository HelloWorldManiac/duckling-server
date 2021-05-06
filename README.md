# Что умеет
Определять даты, числа, email, сайты, должностм, имена/фамилии, города.

# Требования
python 3.6

java

# Docker
Создание образа
```sh
$ docker build -t app-da-chatbot-ml-duckling-image .
```
Запуск контейнера
```sh
$ docker run -d --name app-da-chatbot-ml-duckling -p 8080:8080 -p 8090:8090 app-da-chatbot-ml-duckling-image
```

# Запуск на локальной машине без Docker
Установка python пакетов
```sh
$ pip install -r requirements.txt
```
Запуск
```sh
$ python app.py
```

# Проверка работы
Для проверки работы используем CURL запрос
```sh
curl -d 'text=Вернулась из Италии. Согласно рассылки необходимо оформить отсутствие. Как оформить отсутствие в САП, чтобы эти дни оплачивалис' -u username:hdWN4HtUeL -X POST http://app-da-chatbot-ml-duckling:8080/parse
```
Примерный ответ
```sh
[{"body": "вчера", "dim": "time", "end": 11, "start": 6, "value": {"grain": "day", "type": "value", "value": "2020-04-13T00:00:00.000+04:00", "values": []}}, {"names": [], "places": []}]
```

curl -d 'text=Встречи сегодня до 17' -u username:password -X POST http://localhost:8080/parse