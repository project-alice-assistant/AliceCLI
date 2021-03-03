import click

from . import MainMenu
from .alice import alice
from .install import install
from .utils import commons, utils

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context):
	if ctx.invoked_subcommand is None:
		click.clear()
		ctx.invoke(MainMenu.mainMenu)

cli.add_command(MainMenu.mainMenu)
cli.add_command(commons.connect)
cli.add_command(utils.discover)
cli.add_command(utils.reboot)
cli.add_command(utils.updateSystem)
cli.add_command(utils.upgradeSystem)
cli.add_command(utils.soundTest)
cli.add_command(alice.updateAlice)
cli.add_command(alice.systemctl)
cli.add_command(install.installAlice)
