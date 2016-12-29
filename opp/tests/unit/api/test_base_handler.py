import mock
import unittest

from opp.api import base_handler as bh


class MockConnection(object):
    def cursor(self):
        return None


class MockValue(object):
    def __init__(self, value):
        self.value = value


class TestBaseResponseHandler(unittest.TestCase):

    @mock.patch('pymysql.connect')
    def test_get_payload_missing(self, mock_connect):
        mock_connect.return_value = MockConnection()
        handler = bh.BaseResponseHandler('POST', '', '')
        payload, error = handler._get_payload()
        self.assertEqual(payload, [])
        self.assertEqual(error, {'result': 'error',
                                 'message': 'Payload missing!'})

    @mock.patch('cgi.FieldStorage')
    @mock.patch('pymysql.connect')
    def test_get_payload_invalid(self, mock_connect, mock_cgi):
        mock_connect.return_value = MockConnection()
        mock_cgi.return_value = {'payload': MockValue('blah')}
        handler = bh.BaseResponseHandler('POST', '', '')
        payload, error = handler._get_payload()
        self.assertEqual(payload, [])
        self.assertEqual(error, {'result': 'error',
                                 'message': 'Invalid payload!'})

    @mock.patch('cgi.FieldStorage')
    @mock.patch('pymysql.connect')
    def test_get_payload_empty(self, mock_connect, mock_cgi):
        mock_connect.return_value = MockConnection()
        mock_cgi.return_value = {'payload': MockValue('[]')}
        handler = bh.BaseResponseHandler('POST', '', '')
        payload, error = handler._get_payload()
        self.assertEqual(payload, [])
        self.assertEqual(error, {'result': 'error',
                                 'message': 'Empty payload!'})

    @mock.patch('cgi.FieldStorage')
    @mock.patch('pymysql.connect')
    def test_get_payload(self, mock_connect, mock_cgi):
        mock_connect.return_value = MockConnection()
        mock_cgi.return_value = {'payload': MockValue('["blah"]')}
        handler = bh.BaseResponseHandler('POST', '', '')
        payload, error = handler._get_payload()
        self.assertNotEqual(payload, [])
        self.assertIsNone(error)

    @mock.patch('pymysql.connect')
    def test_respond_bad_method(self, mock_connect):
        mock_connect.return_value = MockConnection()
        for method in ['GET', 'PUT', 'DELETE', 'PATCH']:
            handler = bh.BaseResponseHandler(method, '', '')
            message = "Method %s is not implemented!" % method
            self.assertEqual(handler.respond(),
                             {'result': 'error', 'message': message})

    @mock.patch('pymysql.connect')
    def test_respond_missing_phrase(self, mock_connect):
        mock_connect.return_value = MockConnection()
        handler = bh.BaseResponseHandler('POST', '', '')
        message = "Passphrase missing!"
        self.assertEqual(handler.respond(),
                         {'result': 'error', 'message': message})

    @mock.patch('pymysql.connect')
    def test_respond_missing_action(self, mock_connect):
        mock_connect.return_value = MockConnection()
        handler = bh.BaseResponseHandler('POST', '', '')
        message = "Passphrase missing!"
        self.assertEqual(handler.respond(),
                         {'result': 'error', 'message': message})


class TestErrorResponseHandler(unittest.TestCase):

    def setUp(self):
        self.hndlr = bh.ErrorResponseHandler("some error msg")

    def test_respond(self):
        response = self.hndlr.respond()
        expected = {'message': 'some error msg', 'result': 'error'}
        self.assertEqual(response, expected)
