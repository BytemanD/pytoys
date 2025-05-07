import subprocess
import sys
from urllib import parse

from loguru import logger
import click

from pytoys.common import command
from pytoys.pip import repos
from pytoys.vscode import extension as vscode_extension
from pytoys.github import proxy
from . import cli


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
        vscode_extension.download_extension(name)
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


if __name__ == '__main__':
    sys.exit(cli())
