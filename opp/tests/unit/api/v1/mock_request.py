class MockRequest():
    def __init__(self, method, headers, json):
        MockRequest.method = method
        MockRequest.headers = headers
        MockRequest.json = json

    @staticmethod
    def get_json():
        return MockRequest.json
