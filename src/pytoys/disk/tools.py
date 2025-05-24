import subprocess
import os
import sys
import tempfile
from loguru import logger


def compress_virtual_disk(vhd_path: str):
    """
    使用diskpart压缩虚拟磁盘(VHD/VHDX)

    参数:
        vhd_path (str): 虚拟磁盘文件的完整路径
    """
    # 检查文件是否存在
    if not os.path.exists(vhd_path):
        raise FileNotFoundError(f"虚拟磁盘文件不存在: {vhd_path}")

    # 检查文件扩展名
    if not vhd_path.lower().endswith(('.vhd', '.vhdx')):
        raise ValueError("文件必须是VHD或VHDX格式")

    # 创建diskpart脚本内容
    diskpart_script = f"""
    select vdisk file="{vhd_path}"
    attach vdisk readonly
    compact vdisk
    detach vdisk
    """

    # 临时脚本文件路径
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                     delete=False) as temp_file:
        logger.info("创建临时脚本: {}", temp_file.name)
        temp_file.write(diskpart_script)
        temp_file.flush()  # 确保数据写入文件
        logger.info("写入diskpart脚本")
        temp_script_path = temp_file.name

    if not os.path.exists(temp_script_path):
        raise FileNotFoundError(f"临时脚本文件不存在: {temp_script_path}")

    logger.info("开始压缩虚拟磁盘")

    try:
        # 执行diskpart命令
        subprocess.run(['diskpart', '/s', temp_script_path],
                       stdout=sys.stdout, stderr=sys.stderr,
                       text=True, check=True)
        logger.success("虚拟磁盘 {} 压缩完成", vhd_path)
    finally:
        # 删除临时脚本文件
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)
