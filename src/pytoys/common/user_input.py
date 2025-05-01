from termcolor import colored


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
            return ''
        try:
            index = int(input_index)
            if (min_number is None or index >= min_number) and \
               (max_number is None or index <= max_number):
                return index
            raise ValueError(f'{index} is out of range')
        except ValueError:
            input_index = input(colored('输入错误，请重新输入: ', color='red'))
            input_index = input_index.strip()
