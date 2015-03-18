Задание: разработать приложение для операционных систем семейства
Windows или Linux, обеспечивающее базовые функции сервера протокола
HTTP (Web-сервера). Сервер должен быть написан на языке Python и
уметь обслуживать несколько клиентов одновременно.

Реализуемые методы протокола:

* GET – для передачи Web-страниц и медиа-элементов.

Пример запроса:

    GET / HTTP/1.1
    User-Agent: curl/7.38.0
    Host: MySite
    Accept: */*

Сервер для такого запроса должен обработать имя метода (GET) и запрашиваемый путь (/).
URL должен указывать на реально существующий файл на компьютере, если это не так,
сервер должен выдать ошибку 404 Not Found. Заголовки, такие как Cookie или Host,
не влияют на работу сервера и либо игнорируются, либо отображаются в журнале сервера.

Пример корректного ответа:

    HTTP/1.1 200 OK
    Server: YuryServer
    Date: Wed, 18 Mar 2015 09:06:53 GMT
    Content-Type: text/html
    Content-Length: 168
    Connection: close
    
    Content...

Сервер должен указывать Content-Type (по крайней мере для некоторых известных типов файлов).
Сервер должен указывать заголовок Connection: close и закрывать соединение
 сразу же после выдачи ответа.


Пример ответа на ошибочный запрос:

    HTTP/1.1 404 Not Found
    Server: YuryServer
    Date: Wed, 18 Mar 2015 09:17:47 GMT
    Content-Type: text/html
    Content-Length: 168
    Connection: close
    
    Error description...


* HEAD – аналогично GET, но с передачей клиенту только заголовков,
без выдачи содержимого файла.

Пример ответа:

    HTTP/1.1 200 OK
    Server: nginx/1.4.4
    Date: Wed, 18 Mar 2015 09:21:52 GMT
    Content-Type: text/html; charset=utf-8
    Connection: keep-alive

* POST – для получения от клиента параметров Web-форм.

Сервер должен добавлять в журнал отправляемые данные, а сам запрос обрабатывать как GET.

    POST / HTTP/1.1
    User-Agent: curl/7.38.0
    Host: MySite
    Accept: */*
    Content-Length: 7
    Content-Type: application/x-www-form-urlencoded
    
    abc=abc
