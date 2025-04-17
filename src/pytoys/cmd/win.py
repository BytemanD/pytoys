import sys
import subprocess

import click
from loguru import logger

from pytoys.disk import tools


@click.group()
@click.option("--debug", is_flag=True, help="debug")
def cli(debug):
    """Windows system tools"""
    logger.configure(handlers=[{"sink": sys.stderr,
                                "level": debug and "DEBUG" or "INFO"}])
    pass


@cli.group()
def disk():
    """Disk tools"""
    pass


@disk.command()
@click.argument('vhd_path')
def compress_vhd(vhd_path):
    """Compress vhd/vhdx disk"""
    try:
        tools.compress_virtual_disk(vhd_path)
    except subprocess.CalledProcessError as e:
        logger.error("run diskpart failed")

if __name__ == '__main__':
    cli()
