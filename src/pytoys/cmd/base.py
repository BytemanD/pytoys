import functools
import re
import subprocess
import sys
from concurrent import futures
from typing import Optional
from urllib import parse
import pathlib
from urllib import parse

import click
import requests
import yaml
from loguru import logger
from termcolor import colored, cprint

from pytoys.common import command, httpclient, table
from pytoys.crawler.oneloume.parser import Web1louMe
from pytoys.github import proxy
from pytoys.net import ipinfo, location, utils
from pytoys.net import weather as weather_server
from pytoys.openapi import bingimage, qqmap
from pytoys.pip import repos
from pytoys.vscode import extension as vscode_extension

from . import cli, custome_types, click_command_with_help


@cli.group()
def pip():
    """pip tools"""


@pip.command()
@click.option("--index-url", help="pip源地址")
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
        command.execute(f"pip config set global.index-url {index_url}")
        command.execute(f"pip config set global.trusted-host {url.hostname}")
        logger.success("已设置源: {}", index_url)
        return 0
    except subprocess.CalledProcessError as e:
        logger.error("config pip failed: {}", e)
        return 1


@cli.group()
def vscode():
    """VSCode extension tools"""


@vscode.command()
@click.argument("name")
@click.option("-o", "--output", type=click.Path(), help="保存路径")
def download_extension(name, output=None):
    """下载插件"""
    try:
        api = vscode_extension.MarketplaceAPI()
        api.search_and_download(name, output=output)
        return 0
    except vscode_extension.ExtensionNotFound as e:
        logger.error("download {} failed failed: {}", name, e)
        return 1


@cli.group()
def github():
    """Github tools"""


@github.command()
@click.argument("url")
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
@click.option("--detail", is_flag=True, help="显示详情")
@click.option("--ip", type=custome_types.TYPE_IPV4, help="指定IP地址")
def info(detail=False, ip=None):
    """Get Local info"""
    local_info = {}
    if ip:
        is_ip, ip_type = utils.is_valid_ip(ip)
        if not is_ip or ip_type != utils.V4:
            logger.error("invalid ipv4 address")
            return 1
        local_info["ip"] = ip
    else:
        local_info["ip"] = ipinfo.get_public_api()
    try:
        ip_location = location.Location()
        for api in [location.IP77Api(), location.UUToolApi()]:
            ip_location = api.get_location(local_info.get("ip"))
            break
        if not detail:
            click.echo(f'ip      : {local_info.get("ip")}')
            click.echo(f"location: {ip_location.info()}")
        else:
            local_info.update(**ip_location.to_dict())
            for k, v in local_info.items():
                if not v:
                    continue
                click.echo(f"{k:15}: {v}")
    except IOError as e:
        logger.error("get local info failed: {}", e)
        return 1


@local.command()
@click.option("--city", help="指定城市(省,市,县|区),例如:北京市,东城区")
def weather(city: Optional[str] = None):
    """Get weather"""
    api = weather_server.HefengWeatherApi()
    if not city:
        qq_api = qqmap.QQMapAPIs()
        logger.debug("get my location")
        my_location = qq_api.get_location()
        data = qq_api.get_weather(my_location)
        print(data.format())
        return

    values = re.split(r",|，", city)
    if not values:
        raise ValueError("invalid city")
    if len(values) == 1:
        adm, location_name = None, values[0]
    else:
        adm, location_name = values[0], values[1]
    logger.debug("lookup city {}", city)
    try:
        locations = api.lookup_city(location_name, adm=adm)
    except (httpclient.HttpError, httpclient.RequestError) as e:
        logger.error("lookup city failed: {}", e)
        return 1
    my_location = locations[0]
    data = api.get_weather(my_location)
    print(data.format())


@click_command_with_help
@click.option("-T", "--timeout", type=int, help="Timeout")
@click.option("-M", "--method", help="HTTP method, default: GET", default="GET")
@click.option("-P", "--params", help="HTTP params, e.g. 'key1=value1&key2=value2'")
@click.option("-H", '--header', multiple=True, type=custome_types.TYPE_HEADER,
              help="HTTP headers e.g. 'content-type=application/json")              # fmt: skip
@click.argument("url", default=None)
def curl(url: str, params: Optional[str] = None, method: str = "GET",
         header: Optional[dict] = None, timeout: Optional[int] = None):                 # fmt: skip
    """curl command

    \b
    Argument:
        URl: 请求URL或yaml文件
    Example:
        curl http://www.example.com
        curl @requets.yaml
    """
    if url.startswith('@'):
        file = url.lstrip('@')
        if not pathlib.Path(file).is_file():
            raise click.UsageError(f'file "{file}" not exists')
        with open(file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        reqs = [httpclient.Request.load_from_dict(req) for req in data or []]
    else:
        if not url.startswith('http://') or not url.startswith('https://'):
            raise click.UsageError(
                f'url "{url}" invalid (use http(s)://{url}), or do you want a file? (use @{url}))')

        reqs = [
            httpclient.Request(
                url=url, method=method, params=parse.parse_qs(params or ""),
                headers=functools.reduce(lambda x, y: x | y, header or [], {}),
                timeout=timeout)                                         # fmt: skip
        ]
    for req in reqs:
        cprint(f"========== {req.method} {req.url} ==========", "cyan")
        try:
            resp = httpclient.request(req)
        except requests.exceptions.InvalidSchema:
            cprint("ERROR: invalid url", "red")
            continue
        except (requests.exceptions.SSLError, requests.Timeout, requests.ConnectionError) as e:
            cprint(f"ERROR: request faield: {e}", "red")
            continue

        print(colored(f"{resp.status_code} {resp.reason}",
                      "red" if 400 <= resp.status_code < 600 else "green"))       # fmt: skip
        print()

        for k, v in resp.headers.items():
            print(colored(k, "blue"), ":", v)
        print()

        cprint("Body:", "blue")
        print(resp.content.decode() if resp.content else "")
        # print()
        print(colored(f"Elapsed: {resp.elapsed.total_seconds()}s)", "grey"))

@cli.group()
def crawler():
    """crawler tools"""


@crawler.command()
@click.option("--no-progress", is_flag=True, help="No progress")
@click.option("--date", help="指定年份,格式: YYYY 或 YYYY-MM-DD")
@click.option("--timeout", type=int, default=60 * 5, help="指定timeout")
def bing_image(date: Optional[str] = None, timeout: Optional[int] = None,
                   no_progress: bool=False):                                    # fmt: skip
    """爬取 https://bing.npanuhin.me/ 壁纸"""

    api = bingimage.BingNpanuhinAPI(timeout=timeout)
    logger.info("get images")
    try:
        images = api.get_bing_images(date=date)
    except (httpclient.HttpError, httpclient.RequestError) as e:
        logger.error("get images failed: {}", e)
        return 1
    if not images:
        logger.warning("no images found")
        return 1

    def _download(image: bingimage.BingImage):
        logger.debug("download image: {}", image.filename())
        try:
            api.download_image(image, progress=not no_progress)
        except (httpclient.HttpError, httpclient.RequestError) as e:
            logger.error("download image {} failed: {}", image.filename(), e)

    logger.info("download {} image(s)", len(images))
    with futures.ThreadPoolExecutor() as executor:
        executor.map(_download, images)
    logger.info("download completed")


@crawler.command()
# @click.option("-e", "--exclude", multiple=True, help="按关键字排除")
@click.option("--max-page", type=int, default=1, help="指定最多查询页数")
@click.option("--min-items", type=int, help="最少匹配条数")
@click.option("-t", "--type", multiple=True, help="指定类型")
@click.option("-y", "--year", help="指定年份,格式: 'YYYY' 或 '更早'")
@click.option("-s", "--score", is_flag=True, help="查询评分")
@click.option("--model", default='首页', help="抓取模块")
@click.argument("name", required=False)
def oneloume(year: Optional[str] = None, max_page: Optional[int] = None, name: Optional[str] = None,
             min_items: Optional[int] = None, type: Optional[str]=None,
             score=False, model = None):   # fmt: skip
    """爬取 https://www.1lou.me 视频信息

    NAME: 指定名称
    """

    web = Web1louMe()
    # url = '/'
    models = {
        '首页': '/',
        '电影': 'forum-1.htm',
        '剧集': 'forum-2.htm',
    }
    try:
        videos = web.walk(max_page=max_page, year=year, name=name, min_items=min_items, score=score,
                         media_type=type, progress=True, url=models.get(model))    # fmt: skip
    except httpclient.RequestError as e:
        logger.error("查询失败： {}", e)
        return 1
    fields = ["year", "location", "type", "size", "name", "url"]
    fields.extend(["score_imdb", "score_douban"] if score else [])
    dt = table.DataTable(fields, title={"score_imdb": "IMDB", "score_douban": "豆瓣"}, index=True)
    dt.set_style(table.TableStyle.SINGLE_BORDER)
    dt.set_align({"source": "l", "name": "l", "size": "r", "url": "l", "location": "l"})

    dt.add_object_items(videos)

    # 分页打印
    for page in dt.pages():
        print(page)
    dt.reset_page()


if __name__ == "__main__":
    sys.exit(cli())
