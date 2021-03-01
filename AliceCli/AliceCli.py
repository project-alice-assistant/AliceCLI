import click

from . import MainMenu
from .utils import utils


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
	if ctx.invoked_subcommand is None:
		click.clear()
		MainMenu.mainMenu()

cli.add_command(utils.connect)
cli.add_command(utils.discover)
