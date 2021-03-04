import socket
import time
import click
from PyInquirer import prompt
from networkscan import networkscan

from AliceCli.utils import commons
from AliceCli.utils.decorators import checkConnection


@click.command(name='discover')
@click.option('-n', '--network', required=False, type=str, default='')
@click.option('-a', '--all_devices', is_flag=True)
@click.pass_context
def discover(ctx: click.Context, network: str, all_devices: bool): #NOSONAR
	click.clear()
	click.secho('Discovering devices on your network, please wait', fg='yellow')

	ip = commons.IP_REGEX.search(socket.gethostbyname(socket.gethostname()))
	if not ip and not network:
		commons.printError("Couldn't retrieve local ip address")
	else:
		if not network:
			network = f"{'.'.join(ip[0].split('.')[0:3])}.0/24"

		click.secho(f'Scanning network: {network}', fg='yellow')
		commons.waitAnimation()
		scan = networkscan.Networkscan(network)
		scan.run()

		if all_devices:
			click.secho('Discovered devices:', fg='yellow')
		else:
			click.secho('Discovered potential devices:', fg='yellow')

		devices = list()
		for device in scan.list_of_hosts_found:
			name = socket.gethostbyaddr(device)
			if not name:
				continue

			if all_devices or (not all_devices and ('projectalice' in name[0].lower() or 'raspberrypi' in name[0].lower())):
				click.secho(f'{device}: {name[0].replace(".home", "")}', fg='yellow')
				devices.append(device)

		commons.stopAnimation()

		devices.append('Return to main menu')
		answer = prompt(questions={
			'type'   : 'list',
			'name'   : 'device',
			'message': 'Select the device you want to connect to',
			'choices': devices
		})

		if answer['device'] != 'Return to main menu':
			ctx.invoke(commons.connect, ip_address=answer['device'])

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
