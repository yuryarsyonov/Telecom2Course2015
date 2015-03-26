import mimetypes
import socketserver
from nose import with_setup
from YuryArsyonov.HTTPServer.http_server import start_server
import multiprocessing, time
from nose.tools import assert_equal

__author__ = 'yuryarsyonov'
import requests

class TestServer:
    # @classmethod
    # def setup_class(self):
    #     mimetypes.init()
    #     self.server = start_server()
    #     self.t1 = multiprocessing.Process(target=self.server.serve_forever)
    #     self.t1.start()
    #     while not self.t1.is_alive():
    #         time.sleep(0.1)
    #
    #
    # @classmethod
    # def teardown_class(self):
    #     self.server.shutdown()
    #     self.t1.terminate()

    def test_simple_get(self):
        r = requests.get('http://localhost:8080/mc.yandex.ru/robots.txt')
        assert_equal(r.status_code, 200)
        assert_equal(r.text, "User-Agent: *\nDisallow: /\n")

    def test_file_not_found(self):
        r = requests.get('http://localhost:8080/non/existing/file')
        assert_equal(r.status_code, 404)