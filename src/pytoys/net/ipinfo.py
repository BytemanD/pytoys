from pytoys.common import httpclient


class IPinfoAPI(httpclient.HttpClient):

    def __init__(self):
        super().__init__('https://ipinfo.io', timeout=30)

    def get_public_ip(self) -> str:
        resp = self.get('/json')
        return resp.json().get('ip')


class IPApi(httpclient.HttpClient):

    def __init__(self):
        super().__init__('http://ip-api.com')

    def get_public_ip(self) -> str:
        resp = self.get('/json')
        return resp.json().get('query')
