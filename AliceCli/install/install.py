import click

from AliceCli.utils import commons
from AliceCli.utils.decorators import checkConnection


@click.command(name='installAlice')
@click.pass_context
@checkConnection
def installAlice(ctx: click.Context):
	click.secho('Installing Alice', color='yellow')
	commons.returnToMainMenu(ctx)
