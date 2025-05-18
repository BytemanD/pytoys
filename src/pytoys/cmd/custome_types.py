import dataclasses
import click

from pytoys.net import utils


@dataclasses.dataclass
class Area:
    province: str
    city: str
    district: str


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
                province, city, district = value.split(',')
                return Area(province, city, district)
            except ValueError:
                pass
        self.fail(f"{value} is not a valid area", param, ctx)
        return ''


TYPE_IPV4 = IPv4Type()
TYPE_AREA = AreaType()
