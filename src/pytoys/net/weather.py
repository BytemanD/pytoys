import dataclasses

from pytoys.common import httpclient


@dataclasses.dataclass
class Weather:
    weather: str
    temperature: int|float
    winddirection: str
    windpower: str
    humidity: int|float
    weather: str
    reporttime: str


class XDApi(httpclient.HttpClient):

    def __init__(self):
        super().__init__('http://u.api.xdapi.com')

    def get_weather(self, areacode: str|int) -> Weather:
        resp = self.get('/api/v2/Weather/city', params={'code': areacode})
        data = resp.json()
        if data.get('code') != 1 or not data.get('data'):
            raise ValueError(f'get weather failed, {data.get("msg")}, '
                             f'data: {data.get("data")}')
        value = data.get('data')[0]
        return Weather(
            weather=value.get('weather'),
            temperature=value.get('temperature_float') or \
                value.get('temperature'),
            winddirection=value.get('winddirection'),
            windpower=value.get('windpower'),
            humidity=value.get('humidity_float') or value.get('humidity'),
            reporttime=value.get('reporttime'))
