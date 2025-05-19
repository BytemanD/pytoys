import click
import dataclasses
import re

from pytoys.net import utils


@dataclasses.dataclass
class Area:
    province: str
    city: str
    district: str

    def __str__(self):
        return f"{self.province}-{self.city}-{self.district}"


class IPv4Type(click.ParamType):
    name = "ipv4"

    def convert(self, value, param, ctx) -> str:
        if isinstance(value, str):
            is_ip, ip_type = utils.is_valid_ip(value)
            if is_ip and ip_type == 'v4':
                return value

        self.fail(f"{value} is not a valid ipv4 address", param, ctx)
        return ''


class AreaType(click.ParamType):
    name = "area"

    def convert(self, value, param, ctx) -> Area:
        if isinstance(value, str):
            try:
                province, city, district = re.split(r',|，', value)
                return Area(province, city, district)
            except ValueError:
                pass
        self.fail(f"{value} is not a valid area", param, ctx)
        return ''


TYPE_IPV4 = IPv4Type()
TYPE_AREA = AreaType()
