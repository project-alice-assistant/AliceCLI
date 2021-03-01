import click

from . import MainMenu
from .connect import connect
from .discover import discover


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
	if ctx.invoked_subcommand is None:
		click.clear()
		MainMenu.mainMenu()

cli.add_command(connect.connect)
cli.add_command(discover.discover)
