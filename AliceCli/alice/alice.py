import click

from AliceCli.utils import commons
from AliceCli.utils.decorators import checkConnection


@click.command(name='updateAlice')
@click.pass_context
@checkConnection
def updateAlice(ctx: click.Context):
	click.secho('Updating Alice, please wait', color='yellow')

	commons.waitAnimation()
	commons.SSH.exec_command('sudo systemctl stop ProjectAlice')
	stdin, stdout, stderr = commons.SSH.exec_command('cd ~/ProjectAlice && git pull && git submodules foreach git pull')
	line = stdout.readline()
	while line:
		click.secho(line, nl=False, color='yellow')
		line = stdout.readline()

	commons.SSH.exec_command('sudo systemctl start ProjectAlice')
	commons.printSuccess('Alice updated!')
	commons.returnToMainMenu(ctx)


@click.command(name='do')
@click.option('-o', '--option', required=True, type=click.Choice(['start', 'stop', 'restart', 'enable', 'disable', 'status'], case_sensitive=False))
@click.pass_context
@checkConnection
def systemctl(ctx: click.Context, option: str):
	click.secho(f'Service "{option}", please wait', color='yellow')

	commons.waitAnimation()
	stdin, stdout, stderr = commons.SSH.exec_command(f'sudo systemctl {option} ProjectAlice')
	line = stdout.readline()
	while line:
		click.secho(line, nl=False, color='yellow')
		line = stdout.readline()

	commons.printSuccess('Done!')
	commons.returnToMainMenu(ctx)
