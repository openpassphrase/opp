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

    @mock.patch('cgi.FieldStorage')
    @mock.patch('pymysql.connect')
    def test_respond_missing_action(self, mock_connect, mock_cgi):
        mock_connect.return_value = MockConnection()
        mock_cgi.return_value = {'phrase': MockValue('123')}
        handler = bh.BaseResponseHandler('POST', '', '')
        message = "Action missing!"
        self.assertEqual(handler.respond(),
                         {'result': 'error', 'message': message})

    def _check_called(self, func_name, *exp_args, **exp_kwargs):
        func_name.assert_called_once_with(*exp_args, **exp_kwargs)

    @mock.patch.object(bh.BaseResponseHandler, '_handle_getall')
    @mock.patch('cgi.FieldStorage')
    @mock.patch('pymysql.connect')
    def test_respond_getall(self, mock_connect, mock_cgi, f):
        mock_connect.return_value = MockConnection()
        mock_cgi.return_value = {'phrase': MockValue('123'),
                                 'action': MockValue('getall')}
        handler = bh.BaseResponseHandler('POST', '', '')
        handler.respond()
        self._check_called(bh.BaseResponseHandler._handle_getall, '123')

    @mock.patch.object(bh.BaseResponseHandler, '_handle_create')
    @mock.patch('cgi.FieldStorage')
    @mock.patch('pymysql.connect')
    def test_respond_create(self, mock_connect, mock_cgi, f):
        mock_connect.return_value = MockConnection()
        mock_cgi.return_value = {'phrase': MockValue('123'),
                                 'action': MockValue('create')}
        handler = bh.BaseResponseHandler('POST', '', '')
        handler.respond()
        self._check_called(bh.BaseResponseHandler._handle_create, '123')

    @mock.patch.object(bh.BaseResponseHandler, '_handle_update')
    @mock.patch('cgi.FieldStorage')
    @mock.patch('pymysql.connect')
    def test_respond_update(self, mock_connect, mock_cgi, f):
        mock_connect.return_value = MockConnection()
        mock_cgi.return_value = {'phrase': MockValue('123'),
                                 'action': MockValue('update')}
        handler = bh.BaseResponseHandler('POST', '', '')
        handler.respond()
        self._check_called(bh.BaseResponseHandler._handle_update, '123')

    @mock.patch.object(bh.BaseResponseHandler, '_handle_delete')
    @mock.patch('cgi.FieldStorage')
    @mock.patch('pymysql.connect')
    def test_respond_delete(self, mock_connect, mock_cgi, f):
        mock_connect.return_value = MockConnection()
        mock_cgi.return_value = {'phrase': MockValue('123'),
                                 'action': MockValue('delete')}
        handler = bh.BaseResponseHandler('POST', '', '')
        handler.respond()
        self._check_called(bh.BaseResponseHandler._handle_delete, '123')

    @mock.patch('cgi.FieldStorage')
    @mock.patch('pymysql.connect')
    def test_respond_bad_action(self, mock_connect, mock_cgi):
        mock_connect.return_value = MockConnection()
        mock_cgi.return_value = {'phrase': MockValue('123'),
                                 'action': MockValue('bad')}
        handler = bh.BaseResponseHandler('POST', '', '')
        response = handler.respond()
        expected = {'result': 'error', 'message': 'Action unrecognized!'}
        self.assertEqual(response, expected)


class TestErrorResponseHandler(unittest.TestCase):

    def test_respond(self):
        handler = bh.ErrorResponseHandler("some error msg")
        response = handler.respond()
        expected = {'message': 'some error msg', 'result': 'error'}
        self.assertEqual(response, expected)
