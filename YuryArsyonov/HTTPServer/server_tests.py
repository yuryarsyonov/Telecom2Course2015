import mimetypes
import multiprocessing
from threading import Thread
import time

from nose.tools import assert_equal, raises

from YuryArsyonov.HTTPServer.http_server import start_server


__author__ = 'yuryarsyonov'
import requests

class TestServer:
    correct_url = 'http://localhost:8080/mc.yandex.ru/robots.txt'
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
        r = requests.get(self.correct_url)
        assert_equal(r.status_code, 200)
        assert_equal(r.text, "User-Agent: *\nDisallow: /\n")

    def test_file_not_found(self):
        r = requests.get(self.non_found_url)
        assert_equal(r.status_code, 404)

    def test_head_request(self):
        r = requests.head(self.correct_url)
        assert_equal(r.status_code, 200)

    def test_post_request(self):
        r = requests.post(self.correct_url, data="key=value&abc=abc")
        assert_equal(r.status_code, 200)
        assert_equal(r.text, 'key is value\nabc is abc\n')

    def test_unknown_method(self):
        r = requests.put(self.correct_url)
        assert_equal(r.status_code, 500)