import mimetypes
import os
import socketserver
import urllib.parse
import logging

__author__ = 'yuryarsyonov'

def start_server():
    HOST, PORT = "localhost", 8080

    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler, False)
    server.allow_reuse_address = True
    server.server_bind()
    server.server_activate()
    return server

class Request(object):
    def __init__(self, conn):
        self.headers = {}
        self.conn = conn
        self.req_text = ""

    def fetch_post_params(self):
        assert "Content-Length" in self.headers
        payload_length = int(self.headers["Content-Length"])

        payload = self.req_text.partition('\r\n\r\n')[2]
        while len(payload) < payload_length:
            new_val = self.conn.recv(1024).decode()
            payload += new_val
        response = ""
        for x in payload.split('&'):
            key, equal, value = x.partition('=')
            response += (key + " is " + value + ";")
        logging.info(response)
        return response

    def fetch_request(self):
        self.raw_request = bytearray()
        data = b'tmp'

        while b'\r\n\r\n' not in self.raw_request:
            if not data:
                raise IOError
            data = self.conn.recv(1024)
            logging.info("Received " + data.decode('UTF-8'))
            self.raw_request += data

        self.req_text = self.raw_request.decode("UTF-8")

        raw_headers = self.req_text.splitlines()[1:]
        for header in raw_headers:
            key, sep, value = header.partition(":")
            self.headers[key.strip()] = value.strip()

        logging.info("Request is: \n" + self.req_text)

    def get_req_method(self):
        return self.req_text.partition(' ')[0]

    def get_path(self):
        req_path = self.req_text.splitlines()[0]
        req_path = req_path.partition(' ')[2]
        req_path = req_path.rpartition(' ')[0]

        return urllib.parse.unquote(req_path)

class Response(object):
    def __init__(self):
        self.headers = {}

    def header_add(self, line, value):
        self.headers[line] = value

    def form_message(self, code, message, body,
                      content_type="text/plain", content_encoding=None, send_body=True):
        self.code = code
        self.message = message
        self.header_add("Server", "YuryServer")
        self.header_add("Connection", "close")
        if content_type is not None:
            self.header_add("Content-Type", content_type)
        if content_encoding is not None:
            self.header_add("Content-Encoding", content_encoding)

        self.header_add("Content-Length", str(len(body)))
        if send_body:
            self.body = body
        else:
            self.body = b''

    def send(self, conn):
        conn.send("HTTP/1.1 {} {}\r\n".format(self.code, self.message).encode())
        for key, value in self.headers.items():
            conn.sendall("{}: {}\r\n".format(key, value).encode())
        conn.send(b"\r\n")
        conn.send(self.body)


class MyTCPHandler(socketserver.BaseRequestHandler):
    root = "/home/yuryarsyonov/site/"

    def handle(self):
        req = Request(self.request)
        response = Response()
        try:
            req.fetch_request()

            if req.get_req_method() not in ["GET", "POST", "HEAD"]:
                response.form_message(500, "Internal Server Error", b"")
                response.send(self.request)
                return

            if req.get_req_method() == "POST":
                payload = req.fetch_post_params()
                response.header_add('X-Payload', payload)

            req_path = req.get_path()

            logging.info("Path is" + req_path)
            file_path = self.root + req_path

            file_exists = os.path.isfile(file_path)
            if not file_exists and file_path.endswith('/'):
                file_path += 'index.html'
                file_exists = os.path.isfile(file_path)

            if file_exists:
                (file_type, encoding) = mimetypes.guess_type(file_path)
                file_content = open(file_path, mode='rb').read()

                response.form_message(200, "OK", file_content, content_type=file_type,
                                   content_encoding=encoding,
                                   send_body=req.get_req_method() != 'HEAD')
            else:
                response.form_message(404, "Not Found", b"No such file\r\n")
            response.send(self.request)
        except IOError:
                response.form_message(500, "Internal Server Error", b"")
                response.send(self.request)

        self.request.close()

if __name__ == "__main__":
    mimetypes.init()
    logging.basicConfig(level=logging.DEBUG)
    server = start_server()
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()