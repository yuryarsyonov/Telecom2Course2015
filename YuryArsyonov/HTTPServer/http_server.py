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

class HTTPServer(object):
    root = "/home/yuryarsyonov/site/"
    error_msg = "No such file\r\n".encode('UTF-8')

    def __init__(self):
        self.conn = None

    def header_send(self, line, value):
        self.conn.sendall("{}: {}\r\n".format(line, value).encode('UTF-8'))

    def fetch_post_params(self, request):
        payload_length = -1
        headers = request.splitlines()[1:]
        for header in headers:
            if header.startswith("Content-Length"):
                value = header.partition("Content-Length:")[2]
                value = value.strip()
                payload_length = int(value)
        assert payload_length >= 0
        payload = request.partition('\r\n\r\n')[2]
        while len(payload) < payload_length:
            new_val = self.conn.recv(1024).decode()
            payload += new_val
        response = ""
        for x in payload.split('&'):
            key, equal, value = x.partition('=')
            response += (key + " is " + value + "\n")
        logging.info(response)
        return response

    def fetch_request(self,):
        raw_request = bytearray()

        while b'\r\n\r\n' not in raw_request:
            data = self.conn.recv(1024)
            logging.info("Received " + data.decode('UTF-8'))
            raw_request += data

        return raw_request.decode("UTF-8")

    def get_path(self, request):
        req_path = request.splitlines()[0]
        req_path = req_path.partition(' ')[2]
        req_path = req_path.rpartition(' ')[0]

        return urllib.parse.unquote(req_path)

    def send_response(self, code, message, body,
                      content_type="text/plain", content_encoding=None, send_body=True):
        self.conn.send("HTTP/1.1 {} {}\r\n".format(code, message).encode())
        self.header_send("Server", "YuryServer")
        self.header_send("Connection", "close")
        if content_type is not None:
            self.header_send("Content-Type", content_type)
        if content_encoding is not None:
            self.header_send("Content-Encoding", content_encoding)

        self.header_send("Content-Length", str(len(body)))
        self.conn.send(b"\r\n")
        if send_body:
            self.conn.send(body)

class MyTCPHandler(socketserver.BaseRequestHandler, HTTPServer):
    def handle(self):
        self.conn = self.request

        request = self.fetch_request()
        logging.info("Request is: \n" + request)

        if not (request.startswith("GET ") or
                request.startswith("POST ") or
                request.startswith("HEAD ")):
            self.send_response(500, "Internal Server Error", "".encode())
            return

        if request.startswith("POST "):
            response = self.fetch_post_params(request)
            self.send_response(200, "OK", response.encode())

        req_path = self.get_path(request)

        logging.info("Path is" + req_path)
        file_path = self.root + req_path

        file_exists = os.path.isfile(file_path)
        if not file_exists and file_path.endswith('/'):
            file_path += 'index.html'
            file_exists = os.path.isfile(file_path)

        if file_exists:
            (file_type, encoding) = mimetypes.guess_type(file_path)
            file_content = open(file_path, mode='rb').read()

            self.send_response(200, "OK", file_content, content_type=file_type,
                               content_encoding=encoding,
                               send_body=not request.startswith("HEAD "))
        else:
            self.send_response(404, "Not Found", self.error_msg)

        self.conn.close()

if __name__ == "__main__":
    mimetypes.init()
    logging.basicConfig(level=logging.DEBUG)
    server = start_server()
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()