import mock
import unittest

from opp.api import entries as eh


class MockConnection(object):
    def cursor(self):
        return None


class MockValue(object):
    def __init__(self, value):
        self.value = value


class TestResponseHandler(unittest.TestCase):

    def _check_called(self, func_name, *exp_args, **exp_kwargs):
        func_name.assert_called_once_with(*exp_args, **exp_kwargs)

    @mock.patch.object(eh.ResponseHandler, '_handle_getall')
    @mock.patch('cgi.FieldStorage')
    @mock.patch('pymysql.connect')
    def test_respond_getall(self, mock_connect, mock_cgi, f):
        mock_connect.return_value = MockConnection()
        mock_cgi.return_value = {'phrase': MockValue('123'),
                                 'action': MockValue('getall')}
        handler = eh.ResponseHandler('POST', '', '')
        handler.respond()
        self._check_called(eh.ResponseHandler._handle_getall,
                           '123')

    @mock.patch.object(eh.ResponseHandler, '_handle_create')
    @mock.patch('cgi.FieldStorage')
    @mock.patch('pymysql.connect')
    def test_respond_create(self, mock_connect, mock_cgi, f):
        mock_connect.return_value = MockConnection()
        mock_cgi.return_value = {'phrase': MockValue('123'),
                                 'action': MockValue('create')}
        handler = eh.ResponseHandler('POST', '', '')
        handler.respond()
        self._check_called(eh.ResponseHandler._handle_create,
                           '123')

    @mock.patch.object(eh.ResponseHandler, '_handle_update')
    @mock.patch('cgi.FieldStorage')
    @mock.patch('pymysql.connect')
    def test_respond_update(self, mock_connect, mock_cgi, f):
        mock_connect.return_value = MockConnection()
        mock_cgi.return_value = {'phrase': MockValue('123'),
                                 'action': MockValue('update')}
        handler = eh.ResponseHandler('POST', '', '')
        handler.respond()
        self._check_called(eh.ResponseHandler._handle_update,
                           '123')

    @mock.patch.object(eh.ResponseHandler, '_handle_delete')
    @mock.patch('cgi.FieldStorage')
    @mock.patch('pymysql.connect')
    def test_respond_delete(self, mock_connect, mock_cgi, f):
        mock_connect.return_value = MockConnection()
        mock_cgi.return_value = {'phrase': MockValue('123'),
                                 'action': MockValue('delete')}
        handler = eh.ResponseHandler('POST', '', '')
        handler.respond()
        self._check_called(eh.ResponseHandler._handle_delete,
                           '123')
