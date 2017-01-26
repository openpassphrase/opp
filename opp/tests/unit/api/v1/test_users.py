import mock
import unittest

from opp.api.v1 import users as api


class TestResponseHandler(unittest.TestCase):

    def _check_called(self, func_name, *exp_args, **exp_kwargs):
        func_name.assert_called_once_with(*exp_args, **exp_kwargs)

    @mock.patch('flask.request')
    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(api.ResponseHandler, '_do_get')
    def test_respond_get(self, func, mock_get_session, request):
        request.method = "GET"
        request.headers = {'x-opp-phrase': "123"}
        handler = api.ResponseHandler(request)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('flask.request')
    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(api.ResponseHandler, '_do_put')
    def test_respond_put(self, func, mock_get_session, request):
        request.method = "PUT"
        request.headers = {'x-opp-phrase': "123"}
        handler = api.ResponseHandler(request)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('flask.request')
    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(api.ResponseHandler, '_do_post')
    def test_respond_post(self, func, mock_get_session, request):
        request.method = "POST"
        request.headers = {'x-opp-phrase': "123"}
        handler = api.ResponseHandler(request)
        handler.respond()
        self._check_called(func, '123')

    @mock.patch('flask.request')
    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(api.ResponseHandler, '_do_delete')
    def test_respond_delete(self, func, mock_get_session, request):
        request.method = "DELETE"
        request.headers = {'x-opp-phrase': "123"}
        handler = api.ResponseHandler(request)
        handler.respond()
        self._check_called(func)
