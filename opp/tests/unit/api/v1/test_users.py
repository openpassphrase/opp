import mock
import unittest

from opp.api.v1 import users as api
from test_base_handler import MockRequest, MockSession


class TestResponseHandler(unittest.TestCase):

    def _check_called(self, func_name, *exp_args, **exp_kwargs):
        func_name.assert_called_once_with(*exp_args, **exp_kwargs)

    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(api.ResponseHandler, '_do_get')
    def test_respond_get(self, func, mock_get_session):
        mock_get_session.return_value = MockSession()
        request = MockRequest(phrase="123", method="GET")
        handler = api.ResponseHandler(request)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(api.ResponseHandler, '_do_put')
    def test_respond_put(self, func, mock_get_session):
        mock_get_session.return_value = MockSession()
        request = MockRequest(phrase="123", method="PUT")
        handler = api.ResponseHandler(request)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(api.ResponseHandler, '_do_post')
    def test_respond_post(self, func, mock_get_session):
        mock_get_session.return_value = MockSession()
        request = MockRequest(phrase="123", method="POST")
        handler = api.ResponseHandler(request)
        handler.respond()
        self._check_called(func, '123')

    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(api.ResponseHandler, '_do_delete')
    def test_respond_delete(self, func, mock_get_session):
        mock_get_session.return_value = MockSession()
        request = MockRequest(phrase="123", method="DELETE")
        handler = api.ResponseHandler(request)
        handler.respond()
        self._check_called(func, "123")
