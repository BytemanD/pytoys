import sys

import click
from loguru import logger

from pytoys.code import qrcode as qrcodetools

from . import cli


@cli.group()
def qrcode():
    """QRCode tools"""


@qrcode.command()
@click.argument("text")
@click.option("-o", "--output", default=None, type=click.Path(), help="output file")
def encode(text, output=None):
    """生成二维码"""
    code = qrcodetools.QRCodeExtend()
    code.add_data(text)
    if output:
        code.save(output)
        logger.success("save qrcode to {}", output)
        return 0
    for line in code.parse_string_lines():
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(cli())
