from functools import lru_cache

from pytoys.common import httpclient


# TODO
class XzqhMcaGovApi(httpclient.HttpClient):
    def __init__(self):
        super().__init__('http://xzqh.mca.gov.cn')

    def get_areacode(self, province: str, city: str, district: str) -> str:
        params = {'shengji': [province],
                  'diji': [city],
                  'xianji': [district],
        }
        resp = self.get('/jsp/getInfo.jsp', params=params)
        code = resp.content.decode()
        if not code:
            raise ValueError('code is null')
        return code


class WenyisoApi(httpclient.HttpClient):

    def __init__(self):
        super().__init__('https://www.wenyiso.com')

    @lru_cache()
    def get_areacode_list(self) -> dict:
        resp = self.get('/jres/json/quhuadaima/list.json')
        return resp.json()

    def get_areacode(self, area) -> str:
        arearcodes = self.get_areacode_list()
        code = [k for k, v in arearcodes.items() if v == area]
        if not code:
            raise ValueError(f'area code is not found for {area}')
        return code[0]
