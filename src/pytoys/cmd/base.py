import subprocess
import sys
from urllib import parse

from loguru import logger
import click

from pytoys.common import command
from pytoys.github import proxy
from pytoys.net import areacode
from pytoys.net import ipinfo
from pytoys.net import location
from pytoys.net import weather as weather_server
from pytoys.net import utils
from pytoys.pip import repos
from pytoys.vscode import extension as vscode_extension
from . import cli
from . import custome_types


@cli.group()
def pip():
    """pip tools"""


@pip.command()
@click.option('--index-url', help='pip源地址')
def config_repo(index_url=None):
    """配置pip源"""

    if not index_url:
        index_url = repos.select_repos()
        if not index_url:
            return 1
    url = parse.urlparse(index_url)
    if not url.hostname:
        logger.error("config failed, invalid url: {}", index_url)
        return 1
    try:
        command.execute(f'pip config set global.index-url {index_url}')
        command.execute(f'pip config set global.trusted-host {url.hostname}')
        logger.success("已设置源: {}", index_url)
        return 0
    except subprocess.CalledProcessError as e:
        logger.error("config pip failed: {}", e)
        return 1


@cli.group()
def vscode():
    """VSCode extension tools"""


@vscode.command()
@click.argument('name')
def download_extension(name):
    """下载插件"""
    try:
        api = vscode_extension.MarketplaceAPI()
        api.search_and_download(name)
        return 0
    except vscode_extension.ExtensionNotFound as e:
        logger.error("download {} failed failed: {}", name, e)
        return 1


@cli.group()
def github():
    """Github tools"""


@github.command()
@click.argument('url')
def proxy_download(url):
    """下载github资源"""
    try:
        proxy.download(url)
        logger.success("download {} success", url)
        return 0
    except proxy.AllProxyDownloadFailed as e:
        logger.error("download failed: {}", e)
        return 1


@cli.group()
def local():
    """Local tools"""


@local.command()
@click.option('--detail', is_flag=True, help='显示详情')
@click.option('--ip', type=custome_types.TYPE_IPV4, help='指定IP地址')
def info(detail=False, ip=None):
    """Get Local info"""
    local_info = {}
    if ip:
        is_ip, ip_type = utils.is_valid_ip(ip)
        if not is_ip or ip_type != 'v4':
            logger.error('invalid ipv4 address')
            return 1
        local_info['ip'] = ip
    else:
        local_info['ip'] = ipinfo.get_public_api()
    try:
        ip_location = location.Location()
        for api in [location.IP77Api(), location.UUToolApi()]:
            ip_location = api.get_location(local_info.get('ip'))
            break
        if not detail:
            print(f'ip      : {local_info.get("ip")}')
            print(f'location: {ip_location.info()}')
        else:
            local_info.update(**ip_location.to_dict())
            for k, v in local_info.items():
                if not v:
                    continue
                print(f'{k:15}:', v)
    except IOError as e:
        logger.error("get local info failed: {}", e)
        return 1


# @local.command()
# @click.option('--area', type=custome_types.TYPE_AREA,
#               help='指定区域(省,市,县|区),例如:北京市,北京市,东城区')
# def weather(area: custome_types.Area=None):
#     """Get weather"""
#     if not area:
#         ip_api = ipinfo.IPinfoAPI()
#         public_ip = ip_api.get_public_ip()
#         local_api = location.IP77Api()
#         data = local_api.get_location(public_ip)
#         area = custome_types.Area(data.province, data.city, data.district)

#     api = areacode.XzqhMcaGovApi()
#     code = api.get_areacode(area.province, area.city, area.district)
#     weather_api = weather_server.XDApi()
#     print(weather_api.get_weather(code))


if __name__ == '__main__':
    sys.exit(cli())
