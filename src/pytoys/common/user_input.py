
def get_input_number(message, min_number=None, max_number=None,
                     quit_strs=["exit", 'quit', 'q']):
    """获取用户输入，支持退出功能

    :param message: 提示信息
    :param quit_strs: 退出字符串列表
    :return: 用户输入的整数
    """
    exit_msg = '/'.join(quit_strs)
    input_index = input(f'{message}[输入 {exit_msg} 退出]: ')
    while True:
        if input_index in ['quit', 'exit', 'q']:
            return
        try:
            index = int(input_index)
        except Exception:
            input_index = input('输入错误，请重新输入: ')
            continue
        if (min_number is not None and index >= min_number) and \
           (max_number is not None and index <= max_number):
            return index
        input_index = input('输入错误，请重新输入: ')
