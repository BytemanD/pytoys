import click

from pytoys.net import utils


class IPv4Type(click.ParamType):
    name = "ipv4"

    def convert(self, value, param, ctx) -> str:
        if isinstance(value, str):
            is_ip, ip_type = utils.is_valid_ip(value)
            if is_ip and ip_type == 'v4':
                return value

        self.fail(f"{value} is not a valid ipv4 address", param, ctx)


TYPE_IPV4 = IPv4Type()
