import subprocess

import click
from loguru import logger

from pytoys.common import logging
from pytoys.disk import tools
from pytoys.vscode import extension as vscode_extension


@click.group()
@click.option("--logfile", help="log file")
@click.option("--debug", '-d', is_flag=True, help="debug")
def cli(debug, logfile):
    """Windows system tools"""
    logging.setup_logger(level="DEBUG" if debug else "INFO",
                         file=logfile)


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


@cli.group()
def vscode():
    """VSCode extension tools"""


@vscode.command()
@click.argument('name')
def download_extension(name):
    """Compress vhd/vhdx disk"""
    try:
        vscode_extension.download_extension(name)
    except vscode_extension.ExtensionNotFound as e:
        logger.error("download {} failed failed: {}", name, e)


if __name__ == '__main__':
    cli()           # noqa
