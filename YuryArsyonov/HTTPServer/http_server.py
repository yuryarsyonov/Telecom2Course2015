import mimetypes
import os
import socketserver
import socket
import urllib.parse

__author__ = 'yuryarsyonov'

def fetch_post_params(conn):
    pass

def header_send(conn, line, value):
    conn.sendall("{}: {}\r\n".format(line, value).encode('UTF-8'))

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        conn = self.request
        raw_request = bytearray()

        while b'\r\n\r\n' not in raw_request:
            data = conn.recv(1024)
            print("Received ", data)
            raw_request += data

        request = raw_request.decode("utf-8")
        print("Request is: \n", request)

        assert request.startswith("GET ") or \
               request.startswith("POST ") or \
               request.startswith("HEAD ")

        if request.startswith("POST "):
            fetch_post_params(conn)

        req_path = request.splitlines()[0]
        req_path = req_path.partition(' ')[2]
        req_path = req_path.rpartition(' ')[0]

        req_path = urllib.parse.unquote(req_path)

        print("Path is", req_path)
        root = "/home/yuryarsyonov/site/"
        file_path = root + req_path

        file_exists = os.path.isfile(file_path)
        if not file_exists and file_path.endswith('/'):
            file_path += 'index.html'
            file_exists = os.path.isfile(file_path)
        if file_exists:
            conn.send(b"HTTP/1.1 200 OK\r\n")
        else:
            conn.send(b"HTTP/1.1 404 Not Found\r\n")
        header_send(conn, "Server", "YuryServer")
        header_send(conn, "Connection", "close")
        if file_exists:
            (file_type, encoding) = mimetypes.guess_type(file_path)
            if file_type is not None:
                header_send(conn, "Content-Type", file_type)
            if encoding is not None:
                header_send(conn, "Content-Encoding", encoding)

            file_content = open(file_path, mode='rb').read()
            header_send(conn, "Content-Length", str(len(file_content)))
            conn.send(b"\r\n")
            conn.send(file_content)
        else:
            header_send(conn, "Content-Type", "text/plain")
            error_msg = "No such file\r\n".encode('UTF-8')
            header_send(conn, "Content-Length", str(len(error_msg)))
            conn.send(b"\r\n")
            conn.send(error_msg)
        conn.close()

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    mimetypes.init()

    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    server.allow_reuse_address = True

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
