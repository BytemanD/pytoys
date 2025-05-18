
from pytoys.common import httpclient

# http://u.api.xdapi.com/api/v2/Weather/city?code=500101

class XDApi(httpclient.HttpClient):

    def __init__(self):
        super().__init__('http://u.api.xdapi.com')

    def get_weather(self, areacode: str|int) -> dict:
        
        resp = self.get('/api/v2/Weather/city', params={'code': areacode})
        return resp.content
