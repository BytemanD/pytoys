import dataclasses

import requests

from pytoys.common import httpclient


@dataclasses.dataclass
class Location:
    ip: str = ''
    ip_int: int = None
    isp: str = ''
    continent: str = ''
    country: str = ''
    province: str = ''
    city: str = ''
    district: str = ''
    street: str = ''
    street_history: list = dataclasses.field(default_factory=list)
    # 经度
    longitude: str = ''
    # 纬度
    latitude: str = ''
    area_code: str = ''
    zip_code: str = ''
    location: str = ''
    country_code: str = ''
    time_zone: str = ''

    def info(self):
        if self.location:
            return self.location
        data = f'{self.country}{self.province}{self.city}'
        if self.isp:
            data += f'{data}({self.isp})'
        return data

    def to_dict(self):
        return dataclasses.asdict(self)


class UUToolApi(httpclient.HttpClient):

    def __init__(self):
        super().__init__('https://api.uutool.cn')

    def get_location(self, ipaddr) -> Location:
        resp = self.get(f'/ip/location/?ip={ipaddr}',
                        headers={'accept-language': 'zh-CN'})
        data = resp.json()
        return Location(**data.get('data'))


class IP77Api(httpclient.HttpClient):

    def __init__(self):
        super().__init__('https://api.ip77.net')

    def get_location(self, ipaddr) -> Location:
        resp = self.post('/ip2/v4', data=f'ip={ipaddr}',
                         headers={'content-type': httpclient.TYPE_WWW_FORM})
        body = resp.json()
        if body.get('error'):
            raise IOError(f'request failed {body.get("error")}')
        data = body.get('data', {})
        for k in ['risk']:
            if k not in data:
                continue
            del data[k]
        return Location(**data)
