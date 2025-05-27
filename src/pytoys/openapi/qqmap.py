"""腾讯位置服务 api"""

import hashlib
from typing import Optional
from urllib import parse

from loguru import logger

from pytoys.common import httpclient
from pytoys.net import location, weather


class QQMapAPIs(httpclient.HttpClient):
    """腾讯位置服务 api"""

    def __init__(self, key: Optional[str] = None, signature: Optional[str] = None):
        super().__init__("https://apis.map.qq.com")
        self.key = key or "RKABZ-DCAEB-5VPUG-N4XPP-HGE4K-VXBL6"
        self.signature = signature or "gB38imb0E05bQV8f4aYA2uQVHFfYUFbR"

    def _get_req_params(self, url, params=None) -> dict:
        params = params or {}
        for k, v in params.items() or {}:
            params[k] = v if isinstance(v, list) else [v]
        params["key"] = [self.key]
        # 必须对请求参数进行排序
        sorted_params = {}
        for k in sorted(params.keys()):
            sorted_params[k] = params[k]

        query = parse.urlencode(sorted_params, doseq=True)
        sig = hashlib.md5(f"{url}?{query}{self.signature}".encode("utf-8")).hexdigest()
        sorted_params["sig"] = [sig]
        return sorted_params

    def get_location(self, ip: Optional[str] = None):
        req_url = "/ws/location/v1/ip"
        if ip:
            req_url += f"?ip={ip}"
        params = {"ip": ip} if ip else {}
        params = self._get_req_params(req_url, params)
        logger.debug("req params : {}", params)
        resp = self.get(req_url, params=params)
        result = resp.json().get("result", {})
        return location.Location(
            ip=result.get("ip", ""),
            latitude=result.get("location", {}).get("lat", ""),
            longitude=result.get("location", {}).get("lng", ""),
            country=result.get("ad_info", {}).get("nation", ""),
            province=result.get("ad_info", {}).get("province", ""),
            city=result.get("ad_info", {}).get("city", ""),
            district=result.get("ad_info", {}).get("district", ""),
            area_code=result.get("ad_info", {}).get("adcode", ""),
        )

    def get_weather(self, city: location.Location, query_type: str = "now") -> weather.Weather:
        req_url = "/ws/weather/v1"
        adcode = city.area_code
        params = {"adcode": adcode, "type": query_type}
        params = self._get_req_params(req_url, params)
        logger.debug("req params : {}", params)
        resp = self.get(req_url, params=params)
        result = resp.json().get("result", {})
        realtime = result.get("realtime", [])
        if not realtime:
            raise ValueError("no realtime weather data found")
        realtime = realtime[0]
        return weather.Weather(
            location=city,
            weather=realtime.get("infos", {}).get("weather", ""),
            temperature=realtime.get("infos", {}).get("temperature", ""),
            winddirection=realtime.get("infos", {}).get("wind_direction", ""),
            windpower=realtime.get("infos", {}).get("wind_power", ""),
            humidity=realtime.get("infos", {}).get("humidity", ""),
            reporttime=realtime.get("update_time", ""),
        )


if __name__ == "__main__":
    lbs = QQMapAPIs()
    print(lbs.get_location())
