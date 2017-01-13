import unittest 
import opp.api as api

class FlaskBookshelfTests(unittest.TestCase): 

    @classmethod
    def setUpClass(cls):
        pass 

    @classmethod
    def tearDownClass(cls):
        pass 

    def setUp(self):
        # Create a test client
        self.client = api.app.test_client()
        # propagate exceptions to the test client
        self.client.testing = True 

    def tearDown(self):
        pass 

    def test_health_check(self):
        response = self.client.get('/') 
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(response.data,
                         '{"status": "OpenPassPhrase service is running"}')

    def test_disallowed_methods_categories(self):
        rget = self.client.get('/categories')
        rput = self.client.put('/categories')
        rdel = self.client.delete('/categories')
        rpat = self.client.patch('/categories')
        self.assertEqual(rget.status_code, 405)
        self.assertEqual(rput.status_code, 405)
        self.assertEqual(rdel.status_code, 405)
        self.assertEqual(rpat.status_code, 405)

    def test_disallowed_methods_entries(self):
        rget = self.client.get('/entries')
        rput = self.client.put('/entries')
        rdel = self.client.delete('/entries')
        rpat = self.client.patch('/entries')
        self.assertEqual(rget.status_code, 405)
        self.assertEqual(rput.status_code, 405)
        self.assertEqual(rdel.status_code, 405)
        self.assertEqual(rpat.status_code, 405)

    def test_test(self):
        response = self.client.post('/categories',
                                    data={'phrase': '123', 'action': 'getall'})
