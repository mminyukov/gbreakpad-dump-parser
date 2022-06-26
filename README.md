# Парсинг crash dump на основе google breakpad

Web-сервер написан на python и использует Google Breakpad tools. Повзовляет загружать symbols и парсить dump файлы, чтобы получить читаемый stacktrace вызовов C/C++.

## Goggle Breakpad

Ссылка на проект breakpad на [GitHub](https://github.com/google/breakpad).

Breakpad - это библиотека и набор инструментов, позволяющая предоставлять пользователям приложение без отладочной информации, 
записывать отчеты об ошибках в компактные "минидампы", отправлять их обратно на ваш сервер, а затем создавать читаемый стек вызовов C/C++ из этих минидапмов.

Google Breakpad собирается из исходников и после установки располагается в /usr/local.

## Интерфейс

![image](/images/interface.png)

## Запуск

Для запуска приложения требуется python3, flask и waitress.

Установка flask

```bash
pip3 install flask waitress
```

Запуск приложения
```bash
python3 gbreakpad-dump-parser/main.py
```


### Запуск с помощью **docker** и **docker-compose**

**docker**

Сборка docker образа
```
docker build -t gbreakpad-dump-parser:1.0 .
```

Запуск docker образа
```bash
docker run -d -p5000:5000 --name gbreakpad-dump-parser gbreakpad-dump-parser:1.0
```

Запуск с volume для symbols
```bash
docker run -d -p5000:5000 --name gbreakpad-dump-parser \
  -v /path/to/symbols:/opt/symbols gbreakpad-dump-parser:1.0
```

**docker-compose**

Запуск docker образа через docker-compose
```bash
docker-compose up -d --build
```


## Дополнительно

**Env**

В контейнере доступно несколько переменных окружения:

SERVER_PORT - Порт, на котором будет запущено приложение. Значение по умолчанию: 5000.

SYMBOLS_DEFAULT_PATH - Путь до файлов symbols. Значение по умолчанию: "/opt/symbols".

**CI**

Имеется возможность добавить отправку symbols на этапе CI с помощью bash шага сборки.
```bash
curl -F upload=@symbols.tar.gz -o /dev/null -w 'Response code of uploading debug symbols %{http_code}' http://127.0.0.1:5000/symbols_upload
```