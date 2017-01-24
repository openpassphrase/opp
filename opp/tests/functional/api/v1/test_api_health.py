from . import BackendApiTest


class HealthApiTests(BackendApiTest):

    """These tests exercise the top level request/response functionality of
    the backend API.
    Note: All tests share the same DB, so please beware of
    unintended interaction when adding new tests"""

    def test_health_check(self):
        resp = self._get('/api/v1/health')
        self.assertEqual(resp['status'],
                         "OpenPassPhrase service is running")
