import subprocess
import sys
from urllib import parse

from loguru import logger
import prettytable
from termcolor import cprint

from pytoys.common import command
from pytoys.common import user_input
from . import cli


@cli.group()
def pip():
    """pip tools"""


@pip.command()
def config_repo():
    """配置pip源"""
    repos = [
        ('清华大学', 'https://pypi.tuna.tsinghua.edu.cn/simple'),
        ('阿里云', 'https://mirrors.aliyun.com/pypi/simple'),
        ('中国科技大学', 'https://pypi.mirrors.ustc.edu.cn/simple'),
        ('豆瓣', 'http://pypi.douban.com/simple'),
    ]

    table = prettytable.PrettyTable(['#', "名称", '地址'])
    table.align.update({'#':'r', '名称': 'l', '地址': 'l'})
    for i, (name, repo) in enumerate(repos):
        table.add_row([i+1, name, repo])

    try:
        cprint('选择源:', color='cyan')
        print(table)
        selected = user_input.get_input_number('请输入编号(输入其他表示自定义)')
        if not selected:
            return
        if 1 <= selected <= len(repos):
            input_repo = repos[selected - 1][1]
        else:
            input_repo = input('请输入源地址: ')

        url = parse.urlparse(input_repo)
        if not url.hostname:
            logger.error("config failed, invalid url: {}", input_repo)
            return 1
        command.execute(f'pip config set global.index-url {input_repo}')
        command.execute(f'pip config set global.trusted-host {url.hostname}')
        logger.success("config success")
    except subprocess.CalledProcessError as e:
        logger.error("config pip failed: {}", e)
        return 1


if __name__ == '__main__':
    sys.exit(cli())
