Задание: Разработать приложение для операционных систем семейства Windows
или Linux, обеспечивающее функции клиента протокола SMTP.
Клиент должен быть написан на языке Python.

Приложение должно реализовывать следующие функции:

1. Создание нового письма, включающего такие поля, как
From (отправитель), To (получатель), Subject (тема),
Body (текст)
2. Формирование всех необходимых заголовков письма, с тем, чтобы
приёмная сторона не рассматривала данное письмо как спам.
3. Подключение к указанному SMTP-серверу и отсылка созданного
письма
4. Подробное протоколирование соединения клиента с сервером

Разработанное приложение должно реализовывать следующие команды протокола SMTP:

* HELO/EHLO – передача серверу информации о домене пользователя
* MAIL FROM – передача серверу адреса отправителя письма
* RCPT TO – передача серверу адреса получателя письма
* DATA – передача серверу тела письма
* QUIT – завершение сеанса связи

Диалог между клиентом и сервером должен выглядеть следующим образом:
    
    < 220 smtp18.mail.yandex.net ESMTP (Want to use Yandex.Mail for your domain? Visit http://pdd.yandex.ru)
    > EHLO comp
    < 250-smtp18.mail.yandex.net
    < 250-8BITMIME
    < 250-PIPELINING
    < 250-SIZE 42991616
    < 250-AUTH LOGIN PLAIN
    < 250-DSN
    < 250 ENHANCEDSTATUSCODES
    > AUTH LOGIN
    < 334 VXNlcm5hbWU6
    > ...
    < 334 UGFzc3dvcmQ6
    > ...
    < 235 2.7.0 Authentication successful.
    > MAIL FROM:<yury...@yandex.ru>
    < 250 2.1.0 <yury...@yandex.ru> ok
    > RCPT TO:<yury...@yandex.ru>
    < 250 2.1.5 <yury...@yandex.ru> recipient ok
    > DATA
    < 354 Enter mail, end with "." on a line by itself
    > ...
    < 250 2.0.0 Ok: queued on smtp18.mail.yandex.net as 1426674922-aXGdEk0Xjp-ZLFe7dph
    > QUIT
    < 221 2.0.0 Closing connection.

Логин и пароль кодируются base64. Даныые заканчиваются точкой.
Пример генерируемого сообщения:

    Date: Wed, 18 Mar 2015 13:03:08 +0300
    From: Yury Arsyonov <yury...@yandex.ru>
    Subject: Topic
    To: Yury Arsyonov <yury...@yandex.ru>
    X-Mailer: YuryMailer
    MIME-Version: 1.0
    Content-Type: text/plain
    
    Message!
    