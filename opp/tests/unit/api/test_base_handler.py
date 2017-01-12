import mock
import unittest

from opp.api import base_handler as bh


class MockRequest(object):
    def __init__(self, form):
        self.form = form


class TestBaseResponseHandler(unittest.TestCase):

    def test_get_payload_missing(self):
        request = MockRequest({})
        handler = bh.BaseResponseHandler(request)
        payload, error = handler._get_payload()
        self.assertEqual(payload, [])
        self.assertEqual(error, {'result': 'error',
                                 'message': 'Payload missing!'})

    def test_get_payload_invalid(self):
        request = MockRequest({'payload': 'blah'})
        handler = bh.BaseResponseHandler(request)
        payload, error = handler._get_payload()
        self.assertEqual(payload, [])
        self.assertEqual(error, {'result': 'error',
                                 'message': 'Invalid payload!'})

    def test_get_payload_empty(self):
        request = MockRequest({'payload': '[]'})
        handler = bh.BaseResponseHandler(request)
        payload, error = handler._get_payload()
        self.assertEqual(payload, [])
        self.assertEqual(error, {'result': 'error',
                                 'message': 'Empty payload!'})

    def test_get_payload(self):
        request = MockRequest({'payload': '["blah"]'})
        handler = bh.BaseResponseHandler(request)
        payload, error = handler._get_payload()
        self.assertNotEqual(payload, [])
        self.assertIsNone(error)

    def test_respond_missing_phrase(self):
        request = MockRequest({})
        handler = bh.BaseResponseHandler(request)
        message = "Passphrase missing!"
        self.assertEqual(handler.respond(),
                         {'result': 'error', 'message': message})

    def test_respond_missing_action(self):
        request = MockRequest({'phrase': '123'})
        handler = bh.BaseResponseHandler(request)
        message = "Action missing!"
        self.assertEqual(handler.respond(),
                         {'result': 'error', 'message': message})

    def _check_called(self, func_name, *exp_args, **exp_kwargs):
        func_name.assert_called_once_with(*exp_args, **exp_kwargs)

    @mock.patch.object(bh.BaseResponseHandler, '_handle_getall')
    def test_respond_getall(self, func):
        request = MockRequest({'phrase': '123', 'action': 'getall'})
        handler = bh.BaseResponseHandler(request)
        handler.respond()
        self._check_called(func, '123')

    @mock.patch.object(bh.BaseResponseHandler, '_handle_create')
    def test_respond_create(self, func):
        request = MockRequest({'phrase': '123', 'action': 'create'})
        handler = bh.BaseResponseHandler(request)
        handler.respond()
        self._check_called(bh.BaseResponseHandler._handle_create, '123')

    @mock.patch.object(bh.BaseResponseHandler, '_handle_update')
    def test_respond_update(self, func):
        request = MockRequest({'phrase': '123', 'action': 'update'})
        handler = bh.BaseResponseHandler(request)
        handler.respond()
        self._check_called(func, '123')

    @mock.patch.object(bh.BaseResponseHandler, '_handle_delete')
    def test_respond_delete(self, func):
        request = MockRequest({'phrase': '123', 'action': 'delete'})
        handler = bh.BaseResponseHandler(request)
        handler.respond()
        self._check_called(func, '123')

    def test_respond_bad_action(self):
        request = MockRequest({'phrase': '123', 'action': 'bad'})
        handler = bh.BaseResponseHandler(request)
        response = handler.respond()
        expected = {'result': 'error', 'message': 'Action unrecognized!'}
        self.assertEqual(response, expected)


class TestErrorResponseHandler(unittest.TestCase):

    def test_respond(self):
        handler = bh.ErrorResponseHandler("some error msg")
        response = handler.respond()
        expected = {'message': 'some error msg', 'result': 'error'}
        self.assertEqual(response, expected)
