import click
from pytoys.common import logging


@click.group()
@click.help_option('-h', '--help')
@click.option("--logfile", help="log file")
@click.option("--debug", '-d', is_flag=True, help="debug")
def cli(debug=False, logfile=None):
    """Windows system tools"""
    logging.setup_logger(level="DEBUG" if debug else "INFO",
                         file=logfile)
