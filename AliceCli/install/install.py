import click

from AliceCli.utils import commons
from AliceCli.utils.decorators import checkConnection


@click.command()
@click.pass_context
@checkConnection
def install_alice(ctx: click.Context):
	click.secho('Installing Alice', color='yellow')
	commons.returnToMainMenu(ctx)
