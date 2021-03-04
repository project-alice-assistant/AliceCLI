import time
import click
from PyInquirer import prompt

from AliceCli.utils import commons
from AliceCli.utils.decorators import checkConnection


@click.command(name='changePassword')
@click.option('-c', '--current_password', type=str, required=True)
@click.option('-p', '--password', type=str, required=True)
@click.pass_context
@checkConnection
def changePassword(ctx: click.Context, current_password: str = None, password: str = None):
	click.secho('Changing password', color='yellow')

	if not password or not current_password:
		questions = [
			{
				'type'    : 'password',
				'name'    : 'cpassword',
				'message' : 'Enter current password (default: raspberry)',
				'default' : 'raspberry',
				'validate': lambda pwd: len(pwd) > 0
			},
			{
				'type'    : 'password',
				'name'    : 'npassword',
				'message' : 'Enter new password',
				'validate': lambda pwd: len(pwd) > 0
			},
			{
				'type'    : 'password',
				'name'    : 'npassword2',
				'message' : 'Confirm new password',
				'validate': lambda pwd: len(pwd) > 0
			}
		]

		answers = prompt(questions=questions)

		if not answers:
			commons.returnToMainMenu(ctx)

		if answers['npassword'] != answers['npassword2']:
			commons.printError('New passwords do not match')
			commons.returnToMainMenu(ctx)
			return

		current_password = answers['cpassword']
		password = answers['password']

	commons.waitAnimation()
	stdin, stdout, stderr = commons.SSH.exec_command(f'echo -e "{current_password}\n{password}\n{password}" | passwd')

	error = stderr.readline()
	if 'successfully' in error.lower():
		commons.printSuccess('Password changed!')
	else:
		commons.printError(f'Something went wrong: {error}')

	commons.returnToMainMenu(ctx)


@click.command(name='changeHostname')
@click.option('-n', '--hostname', type=str, callback=commons.validateHostname, required=False)
@click.pass_context
@checkConnection
def changeHostname(ctx: click.Context, hostname: str):
	click.secho('Changing device\'s hostname', color='yellow')

	if not hostname:
		question = [
			{
				'type'    : 'input',
				'name'    : 'hostname',
				'message' : 'Enter new device name',
				'default' : 'ProjectAlice',
				'validate': lambda name: commons.validateHostname(name) is not None
			}
		]

		answer = prompt(questions=question)

		if not answer:
			commons.returnToMainMenu(ctx)

		hostname = answer['hostname']


	commons.waitAnimation()
	commons.SSH.exec_command(f"sudo hostnamectl set-hostname '{hostname}'")
	ctx.invoke(reboot, ctx, return_to_main_menu=False)

	commons.waitAnimation()
	stdin, stdout, stderr = commons.SSH.exec_command('hostname')

	if stdout.readline().lower().strip() == hostname.lower().strip():
		commons.printSuccess('Device name changed!')
	else:
		commons.printError('Failed changing device name...')

	commons.returnToMainMenu(ctx)


@click.command(name='reboot')
@click.pass_context
@checkConnection
def reboot(ctx: click.Context, return_to_main_menu: bool = True): #NOSONAR
	click.secho('Rebooting device, please wait', color='yellow')

	commons.waitAnimation()
	commons.SSH.exec_command('sudo reboot')
	address = commons.CONNECTED_TO
	time.sleep(5)
	while i := 0 < 3: #NOSONAR
		ctx.invoke(commons.connect, ip_address=address, return_to_main_menu=False)
		if commons.SSH:
			commons.printSuccess('Device rebooted!')
			if return_to_main_menu:
				commons.returnToMainMenu(ctx)
			return
		i += 1 #NOSONAR

	commons.printError('Failed rebooting device')

	if return_to_main_menu:
		commons.returnToMainMenu(ctx)


@click.command(name='updateSystem')
@click.pass_context
@checkConnection
def updateSystem(ctx: click.Context):
	click.secho('Updating device\'s system, please wait', color='yellow')

	commons.waitAnimation()
	stdin, stdout, stderr = commons.SSH.exec_command('sudo apt-get update && sudo apt-get upgrade -y')
	line = stdout.readline()
	while line:
		click.secho(line, nl=False, color='yellow')
		line = stdout.readline()

	commons.printSuccess('Device updated!')
	commons.returnToMainMenu(ctx)


@click.command(name='upgradeSystem')
@click.pass_context
@checkConnection
def upgradeSystem(ctx: click.Context):
	click.secho('Upgrading device\'s system, please wait', color='yellow')

	commons.waitAnimation()
	stdin, stdout, stderr = commons.SSH.exec_command('sudo apt-get update && sudo apt-get dist-upgrade -y')
	line = stdout.readline()
	while line:
		click.secho(line, nl=False, color='yellow')
		line = stdout.readline()

	commons.printSuccess('Device upgraded!')
	ctx.invoke(reboot)


@click.command(name='soundtest')
@click.pass_context
@checkConnection
def soundTest(ctx: click.Context):
	click.secho('Testing sound output...', color='yellow')

	commons.waitAnimation()
	stdin, stdout, stderr = commons.SSH.exec_command('sudo aplay /usr/share/sounds/alsa/Front_Center.wav')
	line = stdout.readline()
	commons.stopAnimation()
	click.secho(line)
	commons.returnToMainMenu(ctx)
