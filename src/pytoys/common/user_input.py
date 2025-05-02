from typing import List, Dict

import prettytable
from termcolor import colored, cprint

from pytoys.common import prettytable


def get_input_number(message, min_number=None, max_number=None,
                     quit_strs=None):
    """获取用户输入，支持退出功能

    :param message: 提示信息
    :param quit_strs: 退出字符串列表
    :return: 用户输入的整数
    """
    quit_strs = quit_strs or ['quit', 'exit', 'q']
    exit_msg = '/'.join(quit_strs)
    input_index = input(colored(f'{message}[输入 {exit_msg} 退出]: ', color='cyan'))
    input_index = input_index.strip()
    while True:
        if input_index in quit_strs:
            return 0
        try:
            index = int(input_index)
            if (min_number is None or index >= min_number) and \
               (max_number is None or index <= max_number):
                return index
            raise ValueError(f'{index} is out of range')
        except ValueError:
            input_index = input(colored('输入错误，请重新输入: ', color='red'))
            input_index = input_index.strip()


def select_items(items: List[dict], headers: List[str], title: Dict=None,
                 select_msg: str=None, input_msg: str=None) -> dict:
    """打印items列表, 并获取用户选择结果"""

    title = title or {}
    select_msg = select_msg or '请选择:'
    input_msg = input_msg or '请输入编号'

    table = prettytable.Table(['#'] + [title.get(h, h) for h in headers],
                              style=prettytable.STYLE_LIGHT)
    for i, item in enumerate(items):
        table.add_row([i+1] + [item.get(h) for h in headers])

    cprint(select_msg, color='cyan')
    print(table)
    selected = get_input_number(input_msg, min_number=1, max_number=len(items))
    if not selected:
        return {}
    return items[selected-1]
