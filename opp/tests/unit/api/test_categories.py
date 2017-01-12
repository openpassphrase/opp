import mock
import unittest

from opp.api import categories as ch
from test_base_handler import MockRequest


class TestResponseHandler(unittest.TestCase):

    def _check_called(self, func_name, *exp_args, **exp_kwargs):
        func_name.assert_called_once_with(*exp_args, **exp_kwargs)

    @mock.patch.object(ch.ResponseHandler, '_handle_getall')
    def test_respond_getall(self, func):
        request = MockRequest({'phrase': '123', 'action': 'getall'})
        handler = ch.ResponseHandler(request)
        handler.respond()
        self._check_called(func, '123')

    @mock.patch.object(ch.ResponseHandler, '_handle_create')
    def test_respond_create(self, func):
        request = MockRequest({'phrase': '123', 'action': 'create'})
        handler = ch.ResponseHandler(request)
        handler.respond()
        self._check_called(func, '123')

    @mock.patch.object(ch.ResponseHandler, '_handle_update')
    def test_respond_update(self, func):
        request = MockRequest({'phrase': '123', 'action': 'update'})
        handler = ch.ResponseHandler(request)
        handler.respond()
        self._check_called(func, '123')

    @mock.patch.object(ch.ResponseHandler, '_handle_delete')
    def test_respond_delete(self, func):
        request = MockRequest({'phrase': '123', 'action': 'delete'})
        handler = ch.ResponseHandler(request)
        handler.respond()
        self._check_called(func, '123')
