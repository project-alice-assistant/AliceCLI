import click

from .connect import connect

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
	if ctx.invoked_subcommand is None:
		connect.connect()

cli.add_command(connect.connect)
