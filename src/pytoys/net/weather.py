import dataclasses
import datetime
import time
from functools import lru_cache
from typing import List, Optional

import jwt
from termcolor import colored

from pytoys.common import httpclient

from . import location as net_location

WEATHER_TEMPLATE = """
🕧 {date}     🌎 {area}

  天气: {weather}   🌡️ {temperature}
  风向: {winddirection}
  风力: {windpower}
  风速: {windspeed}
  湿度: {humidity}

  {reporttime}
  {link}
"""


@dataclasses.dataclass
class Weather:
    location: net_location.Location
    weather: str
    temperature: int | float
    winddirection: str
    reporttime: str
    windpower: Optional[str] = None
    # 体感温度
    feels_like: Optional[int | float] = None
    # 风速(公里/小时)
    windspeed: Optional[int] = None
    # 相对湿度，百分比数值
    humidity: Optional[int | float] = None
    link: Optional[str] = None

    def format(self) -> str:
        return WEATHER_TEMPLATE.format(
            date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            area=colored(self.location.info(), "red"),
            weather=colored(self.weather, "cyan"),
            temperature=colored(f"{self.temperature}℃", "cyan"),
            winddirection=colored(self.winddirection, "blue"),
            windpower=colored(self.windpower or "-", "blue"),
            windspeed=colored(self.windspeed or "-", "blue"),
            humidity=colored(self.humidity or "-", "yellow"),
            reporttime=colored(f"更新时间: {self.reporttime}", "grey"),
            link=colored(f"更多信息: {self.link or '-'}", "grey"),
        )


class XDApi(httpclient.HttpClient):

    def __init__(self):
        super().__init__("http://u.api.xdapi.com")

    def get_weather(self, location: net_location.Location) -> Weather:
        resp = self.get("/api/v2/Weather/city", params={"code": location.area_code})
        data = resp.json()
        if data.get("code") != 1 or not data.get("data"):
            raise ValueError(f'get weather failed, {data.get("msg")}, ' f'data: {data.get("data")}')
        value = data.get("data")[0]
        return Weather(
            location=location,
            weather=value.get("weather"),
            temperature=value.get("temperature_float") or value.get("temperature"),
            winddirection=value.get("winddirection"),
            windpower=value.get("windpower"),
            humidity=value.get("humidity_float") or value.get("humidity"),
            reporttime=value.get("reporttime"),
        )


DEFAULT_HEFENG_PROJECT_ID = "482GDEAV8N"
DEFAULT_HEFENG_KID = "KJGUHXCCMM"
DEFAULT_HEFENG_PRIVATE_KEY = """
-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIG+OSUl393SKw7d5kVdWKKp4ViL1EGMs7UCqFAWCs9CU
-----END PRIVATE KEY-----
"""


class HefengWeatherApi(httpclient.HttpClient):

    def __init__(self, project_id: Optional[str]=None, private_key: Optional[str]=None,
                 kid: Optional[str]=None):                                              # fmt: skip
        self.project_id = project_id or DEFAULT_HEFENG_PROJECT_ID
        self.private_key = private_key or DEFAULT_HEFENG_PRIVATE_KEY
        self.kid = kid or DEFAULT_HEFENG_KID
        super().__init__("https://ju44u937u3.re.qweatherapi.com")

    @lru_cache()
    def _get_token(self) -> str:
        payload = {
            "iat": int(time.time()) - 30,
            "exp": int(time.time()) + 900,
            "sub": self.project_id,
        }
        headers = {"kid": self.kid}

        # Generate JWT
        encoded_jwt = jwt.encode(payload, self.private_key, algorithm="EdDSA", headers=headers)
        return encoded_jwt

    @lru_cache
    def lookup_city(self, location: str, adm: Optional[str] = None) -> List[net_location.Location]:
        params = {"location": location}
        if adm:
            params["adm"] = adm
        resp = self.get(
            "/geo/v2/city/lookup",
            params=params,
            headers={"Authorization": f"Bearer {self._get_token()}"},
        )
        locations = resp.json().get("location", [])
        return [
            net_location.Location(
                area_code=x.get("id"),
                country=x.get("country"),
                city=x.get("adm2") or x.get("adm1"),
                district=x.get("name"),
                latitude=x.get("lat"),
                longitude=x.get("lon"),
            )
            for x in locations
        ]

    def get_weather(self, location: net_location.Location) -> Weather:
        resp = self.get("/v7/weather/now", params={"location": location.area_code},
                        headers={"Authorization": f"Bearer {self._get_token()}"})   # fmt: skip
        data = resp.json()
        value = data.get("now")
        return Weather(
            location=location,
            weather=value.get("text"),
            temperature=value.get("temp"),
            winddirection=value.get("windDir"),
            windpower=value.get("windScale"),
            windspeed=value.get("windSpeed"),
            humidity=value.get("humidity"),
            reporttime=data.get("updateTime"),
            link=data.get("fxLink"),
        )
