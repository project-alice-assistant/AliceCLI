import click

from .connect import connect

@click.group()
def cli():
	pass # Project Alice CLI tool

cli.add_command(connect.connect)
