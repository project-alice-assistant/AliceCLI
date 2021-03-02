import click

from AliceCli.utils import commons


@click.command()
def update_alice(ctx: click.Context):
	click.secho('Updating Alice, please wait', color='yellow')

	ssh = commons.checkConnection(ctx)
	if not ssh:
		return

	flag = commons.waitAnimation()
	ssh.exec_command('sudo systemctl stop ProjectAlice')
	stdin, stdout, stderr = ssh.exec_command('cd ~/ProjectAlice && git pull && git submodules foreach git pull')
	line = stdout.readline()
	while line:
		click.secho(line, nl=False, color='yellow')
		line = stdout.readline()

	ssh.exec_command('sudo systemctl start ProjectAlice')
	flag.clear()
	commons.printSuccess('Alice updated!')
	commons.returnToMainMenu(ctx)
