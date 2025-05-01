import prettytable
from termcolor import cprint

from pytoys.common import user_input

repos = [
    ('官方', 'https://pypi.org/simple'),
    ('清华大学', 'https://pypi.tuna.tsinghua.edu.cn/simple'),
    ('中国科技大学', 'https://pypi.mirrors.ustc.edu.cn/simple'),
    ('阿里云', 'https://mirrors.aliyun.com/pypi/simple'),
    ('腾讯', 'http://mirrors.cloud.tencent.com/pypi/simple'),
    ('豆瓣', 'http://pypi.douban.com/simple'),
]


def select_repos() -> str:
    table = prettytable.PrettyTable(['#', "名称", '地址'])
    table.align.update({'#':'r', '名称': 'l', '地址': 'l'})
    for i, (name, repo) in enumerate(repos):
        table.add_row([i+1, name, repo])

    cprint('选择常用pip源:', color='cyan')
    print(table)
    selected = user_input.get_input_number('请输入编号(输入其他表示自定义)')
    if not selected:
        return ''
    return repos[selected - 1][1] if 1 <= selected <= len(repos) else ''
