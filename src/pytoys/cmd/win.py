import subprocess
import sys

import click
from loguru import logger

from pytoys.disk import tools
from . import cli


@cli.group()
def disk():
    """Disk tools"""


@disk.command()
@click.argument('vhd_path')
def compress_vhd(vhd_path):
    """Compress vhd/vhdx disk"""
    try:
        tools.compress_virtual_disk(vhd_path)
    except subprocess.CalledProcessError as e:
        logger.error("run diskpart failed: {}", e)


if __name__ == '__main__':
    sys.exit(cli())
