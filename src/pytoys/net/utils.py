import ipaddress
from typing import Tuple

V4 = "v4"


def is_valid_ip(ip: str) -> Tuple[bool, str]:
    try:
        ipaddress.IPv4Address(ip)
        return True, "v4"
    except ipaddress.AddressValueError:
        pass

    try:
        ipaddress.IPv6Address(ip)
        return True, "v6"
    except ipaddress.AddressValueError:
        pass
    return False, None
