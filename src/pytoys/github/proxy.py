import abc
from typing import List
from urllib import parse

import requests
from loguru import logger


class AllProxyDownloadFailed(Exception):

    def __init__(self, url):
        super().__init__(f"all proxy download {url} failed")


class GitProxyServer(abc.ABC):

    def __init__(self, proxy_url: str):
        self.proxy_url = proxy_url.rstrip("/")

    @abc.abstractmethod
    def get_proxy_urls(self, github_url) -> List[str]:
        """Get proxy url for github url"""


class GhProxy(GitProxyServer):

    def __init__(self):
        super().__init__("https://gh-proxy.com/")

    def get_proxy_urls(self, github_url):
        """Get proxy url for github url"""
        result = parse.urlparse(github_url)
        return [f"{self.proxy_url}/{result.hostname}{result.path}"]


class AkamsProxy(GitProxyServer):

    def __init__(self):
        super().__init__("https://github.akams.cn/")

    def get_proxy_urls(self, github_url):
        """Get proxy url for github url"""
        subproxy_list = ["https://gh.llkk.cc/", "https://github.tbedu.top"]
        return [f"{p}/{github_url}" for p in subproxy_list]


def download(github_url, timeout=60 * 10):
    proxy_list = [GhProxy, AkamsProxy]
    for proxy_cls in proxy_list:
        proxy_driver = proxy_cls()
        logger.info("downlowd with proxy {}", proxy_cls.__name__)
        for proxy_url in proxy_driver.get_proxy_urls(github_url):
            try:
                logger.info("download with proxy url: {}", proxy_url)
                resp = requests.get(proxy_url, timeout=timeout)
            except (
                requests.HTTPError,
                requests.Timeout,
                requests.ConnectionError,
                requests.ConnectTimeout,
            ) as e:
                logger.warning("get with proxy {} failed, {}", proxy_url, e)
                continue

            filename = resp.headers.get("Content-Disposition")
            if filename:
                filename = parse.unquote(filename.split("=")[-1])
            else:
                filename = github_url.split("/")[-1]

            logger.info("save file: {}", filename)
            with open(filename, "wb") as f:
                f.write(resp.content)
            return

    raise AllProxyDownloadFailed(github_url)
