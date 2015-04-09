__author__ = 'yuryarsyonov'

import socket
import base64
import ssl

class SMTPClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def make_header(self, key, value):
        return "{}: {}\r\n".format(key, value)

    def format_message(self, email_from, email_to, subject, data, cc, bcc):
        message = ""
        message += self.make_header("From", email_from)
        message += self.make_header("To", email_to)
        message += self.make_header("Subject", subject)
        if cc:
            message += self.make_header("CC", cc)
        if bcc:
            message += self.make_header("BCC", bcc)
        message += "\r\n"
        message += data
        return message

    def connect(self):
        raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = ssl.wrap_socket(raw_sock)
        self.sock.connect((self.host, self.port))
        self.check_response()

    def command(self, cmd, check_resp=True):
        print(">> " + cmd)
        self.sock.send(cmd.encode() + b"\r\n")
        return self.check_response(check_resp)

    def helo(self, domain):
        self.command("HELO " + domain)

    def auth(self, login, password):
        self.command("AUTH LOGIN", False)
        self.command(base64.b64encode(login.encode()).decode(), False)
        self.command(base64.b64encode(password.encode()).decode())

    def mail_from(self, address):
        self.command("MAIL FROM:<{}>".format(address))

    def rcpt_to(self, address):
        self.command("RCPT TO:<{}>".format(address))

    def data(self, message):
        self.command("DATA", False)
        print("Data: " + message)
        self.sock.send(message.encode() + b"\r\n.\r\n")
        self.check_response()

    def check_response(self, check=True):
        buffer = bytearray()
        while "\r\n" not in buffer.decode():
            new_data = self.sock.recv(1024)
            buffer += new_data
        response = buffer.decode()
        print("<< " + response)
        code = int(response.partition(' ')[0])
        if check:
            assert 200 <= code < 400
        return code

    def quit(self):
        self.command("QUIT")

if __name__ == "__main__":
    host = input("Host: ")
    port_str = input("Port: ")
    if port_str:
        port = int(port_str)
    else:
        port = 465
    domain = socket.getfqdn()

    smtp = SMTPClient(host, port)
    smtp.connect()
    smtp.helo(domain)

    login = input("Login: ")
    password = input("Password: ")
    smtp.auth(login, password)

    email_from = input("Your e-mail: ")
    smtp.mail_from(email_from)

    email_to = input("Recipient e-mail: ")
    email_cc = input("Carbon Copy e-mails: ")
    email_bcc = input("BCC: ")
    for string in [email_to, email_cc, email_bcc]:
        address = string.split(', ')
        for x in address:
            if x:
                smtp.rcpt_to(x.strip())

    email_subject = input("Subject: ")
    data = input("Enter your message: ")
    message = smtp.format_message(email_from=email_from, email_to=email_to, subject=email_subject,
                        cc=email_cc, data=data, bcc=email_bcc)
    smtp.data(message)
    smtp.quit()