import mimetypes
import multiprocessing
from threading import Thread
import time
import io

from nose.tools import assert_equal, raises

from YuryArsyonov.HTTPServer.http_server import start_server, MyTCPHandler


__author__ = 'yuryarsyonov'
import requests

class TestServer:
    file_name = "mc.yandex.ru/robots.txt"
    correct_url = 'http://localhost:8080/' + file_name
    non_found_url = 'http://localhost:8080/non/existing/file'

    @classmethod
    def setup_class(self):
        mimetypes.init()
        self.server = start_server()
        self.t1 = Thread(target=self.server.serve_forever)
        self.t1.daemon = True
        self.t1.start()
        while not self.t1.is_alive():
            time.sleep(0.1)

    def test_simple_get(self):
        file_path = MyTCPHandler.root + self.file_name
        file_content = open(file_path).read()
        r = requests.get(self.correct_url)
        assert_equal(r.status_code, 200)
        assert_equal(r.text, file_content)

    def test_file_not_found(self):
        r = requests.get(self.non_found_url)
        assert_equal(r.status_code, 404)

    def test_head_request(self):
        r = requests.head(self.correct_url)
        assert_equal(r.status_code, 200)

    def test_post_request(self):
        file_path = MyTCPHandler.root + self.file_name
        file_content = open(file_path).read()

        r = requests.post(self.correct_url, data="key=value&abc=abc")
        assert_equal(r.status_code, 200)
        assert_equal(r.headers['X-Payload'], 'key is value;abc is abc;')
        assert_equal(r.text, file_content)

    def mock_socket(self, request):
        input = io.BytesIO(request)
        output = io.BytesIO()
        sock = MockedSocket(input, output)
        handler = MyTCPHandler(sock, None, None)
        handler.handle()
        assert output.getvalue().decode().startswith('HTTP/1.1 500')

    def test_conn_reset(self):
        self.mock_socket(b"GET / HTTP/1.1\r\nContent-Le")

    def test_malformed_request(self):
        self.mock_socket(b"GET/ HTTP/1.1\r\n\r\n")

    def test_unknown_method(self):
        r = requests.put(self.correct_url)
        assert_equal(r.status_code, 500)

class MockedSocket(object):
    def __init__(self, input, output):
        self.input = input
        self.output = output

    def recv(self, num):
        return self.input.read()

    def send(self, data):
        return self.output.write(data)

    def sendall(self, data):
        return self.send(data)

    def close(self):
        pass