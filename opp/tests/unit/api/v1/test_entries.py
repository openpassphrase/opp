import mock
import unittest

from opp.api.v1 import entries as api
from test_base_handler import MockRequest, MockSession


class TestResponseHandler(unittest.TestCase):

    def _check_called(self, func_name, *exp_args, **exp_kwargs):
        func_name.assert_called_once_with(*exp_args, **exp_kwargs)

    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(api.ResponseHandler, '_handle_getall')
    def test_respond_getall(self, func, mock_get_session):
        mock_get_session.return_value = MockSession()
        request = MockRequest({'phrase': '123', 'action': 'getall'})
        handler = api.ResponseHandler(request)
        handler.respond()
        self._check_called(func, '123')

    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(api.ResponseHandler, '_handle_create')
    def test_respond_create(self, func, mock_get_session):
        mock_get_session.return_value = MockSession()
        request = MockRequest({'phrase': '123', 'action': 'create'})
        handler = api.ResponseHandler(request)
        handler.respond()
        self._check_called(func, '123')

    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(api.ResponseHandler, '_handle_update')
    def test_respond_update(self, func, mock_get_session):
        mock_get_session.return_value = MockSession()
        request = MockRequest({'phrase': '123', 'action': 'update'})
        handler = api.ResponseHandler(request)
        handler.respond()
        self._check_called(func, '123')

    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(api.ResponseHandler, '_handle_delete')
    def test_respond_delete(self, func, mock_get_session):
        mock_get_session.return_value = MockSession()
        request = MockRequest({'phrase': '123', 'action': 'delete'})
        handler = api.ResponseHandler(request)
        handler.respond()
        self._check_called(func, '123')
