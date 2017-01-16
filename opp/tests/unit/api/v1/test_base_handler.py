import mock
import unittest

from werkzeug.datastructures import ImmutableMultiDict
from opp.api.v1 import base_handler as bh


class MockRequest(object):
    def __init__(self, method=None, payload=None, phrase=None):
        self.headers = {}

        self.method = method

        if phrase:
            self.headers['x-opp-phrase'] = phrase

        if payload:
            if payload == 'None':
                self.form = ImmutableMultiDict({'payload': None})
            else:
                self.form = ImmutableMultiDict({'payload': payload})
        else:
            self.form = ImmutableMultiDict()


class MockSession(object):
    def close(self):
        pass


class TestBaseResponseHandler(unittest.TestCase):

    def test_check_payload_missing(self):
        request = MockRequest()
        handler = bh.BaseResponseHandler(request)
        payload, error = handler._check_payload(expect_list=True)
        self.assertEqual(payload, None)
        self.assertEqual(error, {'result': "error",
                                 'message': "Payload missing!"})

    def test_check_payload_empty(self):
        request = MockRequest(payload='None')
        handler = bh.BaseResponseHandler(request)
        payload, error = handler._check_payload(expect_list=True)
        self.assertEqual(payload, None)
        self.assertEqual(error, {'result': "error",
                                 'message': "Empty payload!"})

    def test_check_payload_invalid(self):
        request = MockRequest(payload="blah")
        handler = bh.BaseResponseHandler(request)
        payload, error = handler._check_payload(expect_list=True)
        self.assertEqual(payload, None)
        self.assertEqual(error, {'result': "error",
                                 'message': "Invalid payload!"})

    def test_check_payload_list(self):
        request = MockRequest(payload='["blah", "blah"]')
        handler = bh.BaseResponseHandler(request)
        payload, error = handler._check_payload(expect_list=True)
        self.assertNotEqual(payload, None)
        self.assertIsNone(error)

    def test_check_payload_not_list(self):
        request = MockRequest(payload='{"blah": "blah"}')
        handler = bh.BaseResponseHandler(request)
        payload, error = handler._check_payload(expect_list=True)
        self.assertEqual(payload, None)
        self.assertEqual(error,
                         {'result': "error",
                          'message': "Payload should be in list form!"})

    def test_check_payload_obj(self):
        request = MockRequest(payload='{"blah": "blah"}')
        handler = bh.BaseResponseHandler(request)
        payload, error = handler._check_payload(expect_list=False)
        self.assertNotEqual(payload, None)
        self.assertIsNone(error)

    def test_check_payload_not_obj(self):
        request = MockRequest(payload='["blah", "blah"]')
        handler = bh.BaseResponseHandler(request)
        payload, error = handler._check_payload(expect_list=False)
        self.assertEqual(payload, None)
        self.assertEqual(error,
                         {'result': "error",
                          'message': "Payload should not be in list form!"})

    def test_respond_missing_phrase(self):
        request = MockRequest()
        handler = bh.BaseResponseHandler(request)
        self.assertEqual(handler.respond(),
                         {'result': "error",
                         'message': "Passphrase header missing!"})

    def _check_called(self, func_name, *exp_args, **exp_kwargs):
        func_name.assert_called_once_with(*exp_args, **exp_kwargs)

    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_get')
    def test_respond_get(self, func, mock_get_session):
        mock_get_session.return_value = MockSession()
        request = MockRequest(phrase="123", method="GET")
        handler = bh.BaseResponseHandler(request)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_put')
    def test_respond_put(self, func, mock_get_session):
        mock_get_session.return_value = MockSession()
        request = MockRequest(phrase="123", method="PUT")
        handler = bh.BaseResponseHandler(request)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_post')
    def test_respond_update(self, func, mock_get_session):
        mock_get_session.return_value = MockSession()
        request = MockRequest(phrase="123", method="POST")
        handler = bh.BaseResponseHandler(request)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_delete')
    def test_respond_delete(self, func, mock_get_session):
        mock_get_session.return_value = MockSession()
        request = MockRequest(phrase="123", method="DELETE")
        handler = bh.BaseResponseHandler(request)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('opp.db.api.get_session')
    def test_respond_bad_verb(self, mock_get_session):
        mock_get_session.return_value = MockSession()
        request = MockRequest(phrase="123", method="PATCH")
        handler = bh.BaseResponseHandler(request)
        response = handler.respond()
        expected = {'result': "error", 'message': "Method not supported!"}
        self.assertEqual(response, expected)


class TestErrorResponseHandler(unittest.TestCase):

    def test_respond(self):
        handler = bh.ErrorResponseHandler("some error msg")
        response = handler.respond()
        expected = {'message': 'some error msg', 'result': 'error'}
        self.assertEqual(response, expected)
