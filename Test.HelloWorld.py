import torHelloWorld
from tornado.httpclient import AsyncHTTPClient
import tornado.testing
import unittest
from tornado.testing import AsyncTestCase, AsyncHTTPTestCase

class TestHelloApp(AsyncHTTPTestCase):
    def get_app(self):
        return torHelloWorld.make_app()

    def test_homepage(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        print(response.body)
        self.assertEqual(response.body, b'Hello, world')

if __name__ == "__main__":
    unittest.main()
