import functools

import click

from pytoys.common import logging

@click.group()
@click.help_option("-h", "--help")
@click.option("--logfile", help="log file")
@click.option("--debug", "-d", is_flag=True, help="debug")
def cli(debug=False, logfile=None):
    """Pytoys tools"""
    logging.setup_logger(level="DEBUG" if debug else "INFO", file=logfile)


def click_command_with_help(func):

    @cli.command()
    @click.help_option("-h", "--help")
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        func(*args, **kwargs)

    return _wrapper


class MyCommand(click.Command):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params.insert(0, click.Option(
            ["-h", "--help"],
            is_flag=True,
            expose_value=False,
            is_eager=True,
            help="Show this message and exit.",
            callback=self._show_help
        ))

    def _show_help(self, ctx, param, value):
        if value and not ctx.resilient_parsing:
            click.echo(ctx.get_help(), color=ctx.color)
            ctx.exit()
