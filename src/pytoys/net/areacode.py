
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
